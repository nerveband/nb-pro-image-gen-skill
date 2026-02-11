#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "google-genai>=1.0.0",
#     "pillow>=10.0.0",
# ]
# ///
"""
Interactive chat mode for Nano Banana Pro image generation.
Enables multi-turn refinement of images.

Usage:
    uv run chat_image.py
    
Commands:
    /save <filename>     - Save the last generated image
    /config              - Show current configuration
    /aspect <ratio>      - Set aspect ratio (1:1, 16:9, etc.)
    /resolution <size>   - Set resolution (1K, 2K, 4K)
    /thinking <level>    - Set thinking mode (high, medium, low)
    /search              - Toggle Google Search grounding
    /clear               - Clear conversation history
    /help                - Show this help
    exit, quit           - Exit the chat

Example session:
    > Create a logo for "Acme Corp"
    [Image generated]
    > Make the text bolder and add a blue gradient
    [Refined image]
    > /save acme_logo.png
    Saved: /path/to/acme_logo.png
"""

import os
import sys
from pathlib import Path
from datetime import datetime


def get_api_key():
    """Get API key from environment."""
    return os.environ.get("GEMINI_API_KEY")


def main():
    # Check API key
    api_key = get_api_key()
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable not set.", file=sys.stderr)
        sys.exit(1)
    
    # Import after API key check
    from google import genai
    from google.genai import types
    from PIL import Image as PILImage
    from io import BytesIO
    import base64
    
    # Initialize client
    client = genai.Client(api_key=api_key)
    
    # Default configuration
    config = {
        "aspect_ratio": "1:1",
        "resolution": "1K",
        "thinking": "high",
        "search": False,
    }
    
    # Create chat session
    chat = client.chats.create(
        model="gemini-3-pro-image-preview",
        config=types.GenerateContentConfig(
            response_modalities=["TEXT", "IMAGE"],
            image_config=types.ImageConfig(
                aspect_ratio=config["aspect_ratio"],
                image_size=config["resolution"]
            )
        )
    )
    
    print("🍌 Nano Banana Pro - Interactive Chat Mode")
    print("=" * 50)
    print(f"Configuration: aspect={config['aspect_ratio']}, resolution={config['resolution']}, thinking={config['thinking']}")
    print("Type '/help' for commands or start describing your image.\n")
    
    last_image = None
    conversation_turns = 0
    
    while True:
        try:
            # Get user input
            user_input = input("> ").strip()
            
            if not user_input:
                continue
            
            # Handle commands
            if user_input.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break
            
            if user_input.startswith("/"):
                parts = user_input.split(maxsplit=1)
                command = parts[0].lower()
                arg = parts[1] if len(parts) > 1 else ""
                
                if command == "/help":
                    print(__doc__)
                
                elif command == "/config":
                    print(f"Current configuration:")
                    print(f"  Aspect ratio: {config['aspect_ratio']}")
                    print(f"  Resolution: {config['resolution']}")
                    print(f"  Thinking: {config['thinking']}")
                    print(f"  Search: {config['search']}")
                    print(f"  Turns: {conversation_turns}")
                
                elif command == "/aspect":
                    valid_ratios = ["1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9"]
                    if arg in valid_ratios:
                        config["aspect_ratio"] = arg
                        # Recreate chat with new config
                        chat = client.chats.create(
                            model="gemini-3-pro-image-preview",
                            config=types.GenerateContentConfig(
                                response_modalities=["TEXT", "IMAGE"],
                                image_config=types.ImageConfig(
                                    aspect_ratio=config["aspect_ratio"],
                                    image_size=config["resolution"]
                                )
                            )
                        )
                        print(f"Aspect ratio set to: {arg}")
                        print("Note: Chat history cleared due to config change")
                        conversation_turns = 0
                    else:
                        print(f"Invalid aspect ratio. Valid options: {', '.join(valid_ratios)}")
                
                elif command == "/resolution":
                    if arg.upper() in ["1K", "2K", "4K"]:
                        config["resolution"] = arg.upper()
                        print(f"Resolution set to: {config['resolution']}")
                    else:
                        print("Invalid resolution. Options: 1K, 2K, 4K")
                
                elif command == "/thinking":
                    if arg in ["high", "medium", "low"]:
                        config["thinking"] = arg
                        print(f"Thinking mode set to: {arg}")
                    else:
                        print("Invalid thinking level. Options: high, medium, low")
                
                elif command == "/search":
                    config["search"] = not config["search"]
                    print(f"Google Search grounding: {'enabled' if config['search'] else 'disabled'}")
                
                elif command == "/clear":
                    chat = client.chats.create(
                        model="gemini-3-pro-image-preview",
                        config=types.GenerateContentConfig(
                            response_modalities=["TEXT", "IMAGE"],
                            image_config=types.ImageConfig(
                                aspect_ratio=config["aspect_ratio"],
                                image_size=config["resolution"]
                            )
                        )
                    )
                    last_image = None
                    conversation_turns = 0
                    print("Conversation history cleared.")
                
                elif command == "/save":
                    if not last_image:
                        print("No image to save. Generate an image first.")
                        continue
                    
                    if not arg:
                        # Generate timestamped filename
                        timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
                        arg = f"{timestamp}-image.png"
                    
                    save_path = Path(arg)
                    save_path.parent.mkdir(parents=True, exist_ok=True)
                    last_image.save(str(save_path), "PNG")
                    full_path = save_path.resolve()
                    print(f"Saved: {full_path}")
                    print(f"MEDIA: {full_path}")
                
                else:
                    print(f"Unknown command: {command}. Type /help for available commands.")
                
                continue
            
            # Generate image
            print(f"Generating image (aspect: {config['aspect_ratio']}, resolution: {config['resolution']})...")
            
            # Build message config
            message_config = types.GenerateContentConfig(
                image_config=types.ImageConfig(
                    aspect_ratio=config["aspect_ratio"],
                    image_size=config["resolution"]
                )
            )
            
            # Add search if enabled
            if config["search"]:
                message_config.tools = [{"google_search": {}}]
            
            response = chat.send_message(
                user_input,
                config=message_config
            )
            
            conversation_turns += 1
            
            # Process response
            image_saved = False
            for part in response.parts:
                if part.text:
                    print(f"\n{part.text}\n")
                elif part.inline_data:
                    # Convert inline data to PIL Image
                    image_data = part.inline_data.data
                    if isinstance(image_data, str):
                        image_data = base64.b64decode(image_data)
                    
                    image = PILImage.open(BytesIO(image_data))
                    last_image = image
                    
                    # Save to temp file for display
                    temp_path = Path(f"/tmp/nano-banana-chat-{conversation_turns}.png")
                    if image.mode == 'RGBA':
                        rgb_image = PILImage.new('RGB', image.size, (255, 255, 255))
                        rgb_image.paste(image, mask=image.split()[3])
                        rgb_image.save(str(temp_path), 'PNG')
                    elif image.mode == 'RGB':
                        image.save(str(temp_path), 'PNG')
                    else:
                        image.convert('RGB').save(str(temp_path), 'PNG')
                    
                    print(f"✓ Image generated (Turn {conversation_turns})")
                    print(f"  Size: {image.size[0]}x{image.size[1]}")
                    print(f"  Use '/save <filename>' to save this image")
                    image_saved = True
            
            if not image_saved:
                print("No image was generated in the response.")
        
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
