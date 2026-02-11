#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "google-genai>=1.0.0",
#     "pillow>=10.0.0",
# ]
# ///
"""
Generate images using Google's Nano Banana Pro (Gemini 3 Pro Image) API.

Usage:
    uv run generate_image.py --prompt "your image description" --filename "output.png"

Multi-image editing (up to 14 images):
    uv run generate_image.py --prompt "combine these images" --filename "output.png" -i img1.png -i img2.png

Quick examples:
    # Logo with proper aspect ratio
    uv run generate_image.py -p "Clean minimalist logo" -f logo.png --aspect 1:1
    
    # Cinematic shot with thinking mode
    uv run generate_image.py -p "Epic landscape" -f scene.png --aspect 16:9 --thinking high
    
    # Edit existing image
    uv run generate_image.py -p "Add sunset background" -f edited.png -i photo.png
"""

import argparse
import os
import sys
from pathlib import Path


# Prompt templates for common use cases
TEMPLATES = {
    "photorealistic": (
        "{subject}, {action}, in {setting}, shot from {camera_angle}. "
        "Photorealistic style with {lighting}, {lens} lens. {mood}. "
        "Ultra high detail, sharp focus, professional photography."
    ),
    "product": (
        "Professional product photo of {product} on {surface}, "
        "{lighting} setup, {angle}, {style} aesthetic, "
        "high-end commercial photography, sharp focus."
    ),
    "logo": (
        "Clean {style} logo featuring {elements}, {colors}, "
        "{typography}, minimalist design on {background}, "
        "vector style, scalable."
    ),
    "social": (
        "Vertical {aspect} social media graphic. "
        "Top: {headline}. Middle: {visual}. Bottom: {details}. "
        "Bold typography, high contrast, engaging layout."
    ),
    "portrait": (
        "Professional portrait of {subject}, {pose}, "
        "shot with {lens} lens, {lighting}, "
        "{background} background, {mood} atmosphere, "
        "high fashion editorial style."
    ),
}


def apply_template(template_name: str, **kwargs) -> str:
    """Apply a prompt template with the given parameters."""
    if template_name not in TEMPLATES:
        raise ValueError(f"Unknown template: {template_name}. Available: {list(TEMPLATES.keys())}")
    try:
        return TEMPLATES[template_name].format(**kwargs)
    except KeyError as e:
        raise ValueError(f"Missing required parameter for {template_name} template: {e}")


def get_api_key(provided_key: str | None) -> str | None:
    """Get API key from argument first, then environment."""
    if provided_key:
        return provided_key
    return os.environ.get("GEMINI_API_KEY")


def get_smart_defaults(prompt: str):
    """Auto-detect recommended settings based on prompt content."""
    prompt_lower = prompt.lower()
    defaults = {"aspect_ratio": "1:1", "thinking": "high", "add_text_guidance": False}
    
    # Detect use case
    if any(word in prompt_lower for word in ["logo", "icon", "emblem"]):
        defaults["aspect_ratio"] = "1:1"
        defaults["thinking"] = "high"
        defaults["add_text_guidance"] = True
    elif any(word in prompt_lower for word in ["portrait", "headshot", "person"]):
        defaults["aspect_ratio"] = "3:4"
        defaults["thinking"] = "high"
    elif any(word in prompt_lower for word in ["landscape", "scenic", "panorama", "cinematic"]):
        defaults["aspect_ratio"] = "16:9"
    elif any(word in prompt_lower for word in ["story", "reel", "tiktok", "vertical"]):
        defaults["aspect_ratio"] = "9:16"
    elif any(word in prompt_lower for word in ["product", "mockup", "packaging"]):
        defaults["aspect_ratio"] = "4:3"
        defaults["thinking"] = "high"
        defaults["add_text_guidance"] = True
    elif any(word in prompt_lower for word in ["infographic", "diagram", "chart"]):
        defaults["aspect_ratio"] = "16:9"
        defaults["thinking"] = "high"
        defaults["add_text_guidance"] = True
    
    return defaults


def validate_prompt(prompt: str) -> list:
    """Check for common pitfalls and return warnings."""
    warnings = []
    prompt_lower = prompt.lower()
    
    # Check for text-heavy prompts
    text_indicators = ["text", "font", "typography", "label", "title", "heading"]
    text_count = sum(1 for indicator in text_indicators if indicator in prompt_lower)
    if text_count > 3:
        warnings.append("⚠️  Warning: You have many text elements. Limit to 1-3 for best results.")
    
    # Check for conflicting styles
    style_conflicts = [
        (["photorealistic", "realistic", "photo"], ["cartoon", "anime", "illustration", "sketch"]),
        (["oil painting", "painting"], ["3d render", "cgi", "digital art"]),
    ]
    for realistic, stylized in style_conflicts:
        has_realistic = any(s in prompt_lower for s in realistic)
        has_stylized = any(s in prompt_lower for s in stylized)
        if has_realistic and has_stylized:
            warnings.append("⚠️  Warning: Conflicting styles detected (e.g., photorealistic + cartoon). Pick one for best results.")
            break
    
    # Check for vague prompts
    vague_indicators = ["nice", "good", "beautiful", "cool"]
    if any(word in prompt_lower for word in vague_indicators) and len(prompt.split()) < 10:
        warnings.append("⚠️  Warning: Prompt is vague. Add specific details about subject, lighting, camera angle, and style.")
    
    return warnings


def main():
    parser = argparse.ArgumentParser(
        description="Generate images using Nano Banana Pro (Gemini 3 Pro Image)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic generation
  uv run generate_image.py -p "A serene mountain landscape" -f mountain.png
  
  # With aspect ratio and thinking mode
  uv run generate_image.py -p "Epic cityscape" -f city.png --aspect 21:9 --thinking high
  
  # Edit existing image
  uv run generate_image.py -p "Add sunset colors" -f sunset.png -i photo.png
  
  # Multi-image composition
  uv run generate_image.py -p "Group photo" -f group.png -i person1.png -i person2.png -i person3.png
  
  # Use template
  uv run generate_image.py --template photorealistic -f photo.png --template-var subject="A cat" --template-var action="sleeping"
        """
    )
    
    # Core arguments
    parser.add_argument(
        "--prompt", "-p",
        help="Image description/prompt (use quotes for multi-word)"
    )
    parser.add_argument(
        "--filename", "-f",
        required=True,
        help="Output filename (e.g., sunset-mountains.png)"
    )
    
    # Input/output options
    parser.add_argument(
        "--input-image", "-i",
        action="append",
        dest="input_images",
        metavar="IMAGE",
        help="Input image path(s) for editing/composition. Can be specified multiple times (up to 14 images)."
    )
    parser.add_argument(
        "--resolution", "-r",
        choices=["1K", "2K", "4K"],
        default="1K",
        help="Output resolution: 1K (default), 2K, or 4K"
    )
    parser.add_argument(
        "--aspect", "-a",
        choices=["1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9"],
        help="Aspect ratio (auto-detected if not specified)"
    )
    
    # Advanced options
    parser.add_argument(
        "--thinking",
        choices=["high", "medium", "low"],
        default="high",
        help="Thinking mode: high=best quality/slower (default), low=faster"
    )
    parser.add_argument(
        "--system",
        "-s",
        help="System prompt for consistent constraints across all generations"
    )
    parser.add_argument(
        "--search",
        action="store_true",
        help="Enable Google Search grounding for real-time data"
    )
    
    # Template options
    parser.add_argument(
        "--template",
        choices=list(TEMPLATES.keys()),
        help="Use a predefined prompt template"
    )
    parser.add_argument(
        "--template-var",
        action="append",
        metavar="KEY=VALUE",
        help="Template variables (e.g., --template-var subject='A cat'). Can be used multiple times."
    )
    
    # Utility options
    parser.add_argument(
        "--smart",
        action="store_true",
        help="Apply smart defaults based on prompt content"
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        default=True,
        help="Validate prompt and show warnings (default: True)"
    )
    parser.add_argument(
        "--no-validate",
        action="store_true",
        help="Skip prompt validation"
    )
    parser.add_argument(
        "--api-key", "-k",
        help="Gemini API key (overrides GEMINI_API_KEY env var)"
    )

    args = parser.parse_args()
    
    # Handle template
    if args.template:
        if not args.template_var:
            print(f"Error: --template requires --template-var arguments", file=sys.stderr)
            print(f"Template '{args.template}' requires these variables. Example:", file=sys.stderr)
            # Extract required vars from template
            template = TEMPLATES[args.template]
            import re
            vars_needed = re.findall(r'\{(\w+)\}', template)
            print(f"  --template-var {vars_needed[0]}='value' --template-var {vars_needed[1]}='value' ...", file=sys.stderr)
            sys.exit(1)
        
        template_vars = {}
        for var in args.template_var:
            if '=' not in var:
                print(f"Error: Template variable must be in format KEY=VALUE: {var}", file=sys.stderr)
                sys.exit(1)
            key, value = var.split('=', 1)
            template_vars[key] = value
        
        try:
            args.prompt = apply_template(args.template, **template_vars)
            print(f"Generated prompt from template: {args.prompt[:100]}...")
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    
    if not args.prompt:
        print("Error: --prompt or --template is required", file=sys.stderr)
        sys.exit(1)
    
    # Apply smart defaults
    if args.smart or not args.aspect:
        smart_defaults = get_smart_defaults(args.prompt)
        if not args.aspect:
            args.aspect = smart_defaults["aspect_ratio"]
            print(f"Auto-selected aspect ratio: {args.aspect}")
        if smart_defaults.get("add_text_guidance") and "text" not in args.prompt.lower():
            args.prompt += " Ensure any text is large, bold, and highly readable."
            print("Added text rendering guidance to prompt")
    
    # Validate prompt
    if args.validate and not args.no_validate:
        warnings = validate_prompt(args.prompt)
        for warning in warnings:
            print(warning, file=sys.stderr)
    
    # Show configuration
    print(f"\nConfiguration:")
    print(f"  Resolution: {args.resolution}")
    print(f"  Aspect ratio: {args.aspect}")
    print(f"  Thinking: {args.thinking}")
    if args.search:
        print(f"  Google Search: enabled")
    if args.system:
        print(f"  System prompt: {args.system[:50]}...")
    print()

    # Get API key
    api_key = get_api_key(args.api_key)
    if not api_key:
        print("Error: No API key provided.", file=sys.stderr)
        print("Please either:", file=sys.stderr)
        print("  1. Provide --api-key argument", file=sys.stderr)
        print("  2. Set GEMINI_API_KEY environment variable", file=sys.stderr)
        sys.exit(1)

    # Import here after checking API key to avoid slow import on error
    from google import genai
    from google.genai import types
    from PIL import Image as PILImage

    # Initialise client
    client = genai.Client(api_key=api_key)

    # Set up output path
    output_path = Path(args.filename)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Load input images if provided (up to 14 supported by Nano Banana Pro)
    input_images = []
    output_resolution = args.resolution
    if args.input_images:
        if len(args.input_images) > 14:
            print(f"Error: Too many input images ({len(args.input_images)}). Maximum is 14.", file=sys.stderr)
            sys.exit(1)

        max_input_dim = 0
        for img_path in args.input_images:
            try:
                img = PILImage.open(img_path)
                input_images.append(img)
                print(f"Loaded input image: {img_path}")

                # Track largest dimension for auto-resolution
                width, height = img.size
                max_input_dim = max(max_input_dim, width, height)
            except Exception as e:
                print(f"Error loading input image '{img_path}': {e}", file=sys.stderr)
                sys.exit(1)

        # Auto-detect resolution from largest input if not explicitly set
        if args.resolution == "1K" and max_input_dim > 0:  # Default value
            if max_input_dim >= 3000:
                output_resolution = "4K"
            elif max_input_dim >= 1500:
                output_resolution = "2K"
            else:
                output_resolution = "1K"
            print(f"Auto-detected resolution: {output_resolution} (from max input dimension {max_input_dim})")

    # Build contents (images first if editing, prompt only if generating)
    if input_images:
        contents = [*input_images, args.prompt]
        img_count = len(input_images)
        print(f"Processing {img_count} image{'s' if img_count > 1 else ''} with resolution {output_resolution}...")
    else:
        contents = args.prompt
        print(f"Generating image with resolution {output_resolution}...")

    # Build config
    image_config_params = {"image_size": output_resolution}
    if args.aspect:
        image_config_params["aspect_ratio"] = args.aspect
    
    config = types.GenerateContentConfig(
        response_modalities=["TEXT", "IMAGE"],
        image_config=types.ImageConfig(**image_config_params)
    )
    
    # Note: Thinking mode is built into Gemini 3 Pro Image and cannot be disabled
    # The --thinking flag is kept for compatibility but doesn't change behavior
    
    # Add system instruction if provided
    if args.system:
        config.system_instruction = args.system
    
    # Add search grounding if enabled
    if args.search:
        config.tools = [{"google_search": {}}]
    
    try:
        response = client.models.generate_content(
            model="gemini-3-pro-image-preview",
            contents=contents,
            config=config
        )

        # Process response and convert to PNG
        image_saved = False
        for part in response.parts:
            if part.text is not None:
                print(f"Model response: {part.text}")
            elif part.inline_data is not None:
                # Convert inline data to PIL Image and save as PNG
                from io import BytesIO

                # inline_data.data is already bytes, not base64
                image_data = part.inline_data.data
                if isinstance(image_data, str):
                    # If it's a string, it might be base64
                    import base64
                    image_data = base64.b64decode(image_data)

                image = PILImage.open(BytesIO(image_data))

                # Ensure RGB mode for PNG (convert RGBA to RGB with white background if needed)
                if image.mode == 'RGBA':
                    rgb_image = PILImage.new('RGB', image.size, (255, 255, 255))
                    rgb_image.paste(image, mask=image.split()[3])
                    rgb_image.save(str(output_path), 'PNG')
                elif image.mode == 'RGB':
                    image.save(str(output_path), 'PNG')
                else:
                    image.convert('RGB').save(str(output_path), 'PNG')
                image_saved = True

        if image_saved:
            full_path = output_path.resolve()
            print(f"\nImage saved: {full_path}")
            # Moltbot parses MEDIA tokens and will attach the file on supported providers.
            print(f"MEDIA: {full_path}")
        else:
            print("Error: No image was generated in the response.", file=sys.stderr)
            sys.exit(1)

    except Exception as e:
        print(f"Error generating image: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
