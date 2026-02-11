# NB Pro Image Gen Skill

A comprehensive, AI-friendly toolkit for professional image generation using Google's Gemini 3 Pro Image (Nano Banana Pro) API.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Made by [Ashraf Ali](https://ashrafali.net)

## ✨ Features

- **🎨 Multi-Mode Generation**: Text-to-image, image editing, and multi-image composition
- **📐 Aspect Ratio Control**: Full support for 1:1, 16:9, 9:16, 4:3, 3:2, 21:9, and more
- **🧠 Smart Defaults**: Auto-detects optimal settings based on your prompt
- **📝 Prompt Templates**: Pre-built templates for logos, products, portraits, and more
- **💬 Interactive Chat Mode**: Multi-turn refinement with conversation history
- **🔍 Validation & Warnings**: Catches common pitfalls before generation
- **🎯 System Prompts**: Enforce consistent styles across all generations
- **🔎 Google Search Grounding**: Real-time data for infographics and current events

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/nerveband/nb-pro-image-gen-skill.git
cd nb-pro-image-gen-skill

# Set your API key
export GEMINI_API_KEY="your-api-key-here"
```

### Generate Your First Image

```bash
# Basic generation
uv run scripts/generate_image.py \
  -p "A serene mountain landscape at sunset" \
  -f landscape.png

# With aspect ratio
uv run scripts/generate_image.py \
  -p "Epic cinematic cityscape" \
  -f city.png \
  --aspect 21:9

# Using a template
uv run scripts/generate_image.py \
  --template photorealistic \
  --template-var subject="A majestic lion" \
  --template-var action="roaring" \
  --template-var setting="African savanna" \
  -f lion.png
```

## 📚 Documentation

- [Complete Usage Guide](#usage-guide)
- [Prompt Templates](#prompt-templates)
- [Best Practices](#best-practices)
- [API Reference](#api-reference)
- [Examples](#examples)

## 🔧 Usage Guide

### Basic Image Generation

```bash
uv run scripts/generate_image.py \
  --prompt "Your description here" \
  --filename output.png
```

### Aspect Ratios

Supported ratios: `1:1`, `2:3`, `3:2`, `3:4`, `4:3`, `4:5`, `5:4`, `9:16`, `16:9`, `21:9`

```bash
# Social media story (vertical)
uv run scripts/generate_image.py \
  -p "Quote graphic with bold typography" \
  -f story.png \
  --aspect 9:16

# Cinematic widescreen
uv run scripts/generate_image.py \
  -p "Movie poster design" \
  -f poster.png \
  --aspect 21:9
```

### Smart Defaults

Enable automatic setting detection based on prompt content:

```bash
uv run scripts/generate_image.py \
  -p "Professional headshot for LinkedIn" \
  -f portrait.png \
  --smart
# Auto-selects: aspect=3:4, thinking=high
```

Auto-detection works for:
- **Logos** → 1:1 aspect, text optimization
- **Portraits** → 3:4 aspect, high quality
- **Landscapes** → 16:9 aspect
- **Products** → 4:3 aspect, commercial style
- **Social media** → 9:16 or 1:1 aspect

### Image Editing

Edit existing images with text instructions:

```bash
uv run scripts/generate_image.py \
  -p "Add dramatic sunset colors and lens flare" \
  -f edited.png \
  -i original.png
```

### Multi-Image Composition

Combine up to 14 reference images:

```bash
uv run scripts/generate_image.py \
  -p "Family portrait with everyone smiling" \
  -f family.png \
  -i person1.png -i person2.png -i person3.png
```

### Interactive Chat Mode

Perfect for iterative refinement:

```bash
uv run scripts/chat_image.py
```

Example session:
```
> Create a logo for my coffee shop "Daily Grind"
[Image generated]
> Make it more minimalist and use earth tones
[Refined image]
> Add a coffee bean icon above the text
[Refined image]
> /save daily_grind_logo.png
Saved: /path/to/daily_grind_logo.png
```

**Chat Commands:**
- `/save <filename>` - Save the last generated image
- `/aspect <ratio>` - Change aspect ratio (clears history)
- `/resolution <size>` - Set resolution (1K, 2K, 4K)
- `/search` - Toggle Google Search grounding
- `/clear` - Clear conversation history
- `/config` - Show current settings
- `/help` - Show help
- `exit` or `quit` - Exit chat

## 📝 Prompt Templates

Use structured templates for consistent, professional results:

### Available Templates

**photorealistic**: Professional photography with camera specs
```bash
uv run scripts/generate_image.py \
  --template photorealistic \
  --template-var subject="A majestic lion" \
  --template-var action="roaring" \
  --template-var setting="African savanna at golden hour" \
  --template-var camera_angle="low angle shot" \
  --template-var lighting="warm golden hour backlighting" \
  --template-var lens="200mm telephoto" \
  --template-var mood="powerful and majestic" \
  -f lion.png
```

**product**: E-commerce product photography
```bash
uv run scripts/generate_image.py \
  --template product \
  --template-var product="artisan coffee beans in kraft bag" \
  --template-var surface="rustic wooden table" \
  --template-var lighting="soft natural window light" \
  --template-var angle="45-degree angle" \
  --template-var style="minimalist lifestyle" \
  -f coffee.png
```

**logo**: Clean logo designs
```bash
uv run scripts/generate_image.py \
  --template logo \
  --template-var style="minimalist" \
  --template-var elements="coffee bean and steam" \
  --template-var colors="black and white" \
  --template-var typography="sans-serif" \
  --template-var background="white" \
  -f logo.png
```

**portrait**: Professional portraits
```bash
uv run scripts/generate_image.py \
  --template portrait \
  --template-var subject="confident businesswoman" \
  --template-var pose="three-quarter view" \
  --template-var lens="85mm" \
  --template-var lighting="soft studio lighting" \
  --template-var background="neutral gray" \
  --template-var mood="professional and approachable" \
  -f portrait.png
```

**social**: Social media graphics
```bash
uv run scripts/generate_image.py \
  --template social \
  --template-var aspect="9:16" \
  --template-var headline="Summer Sale" \
  --template-var visual="beach sunset with palm trees" \
  --template-var details="50% OFF - This Weekend Only" \
  -f instagram_story.png
```

## 🎯 Best Practices

### The 5 Essential Elements

Every prompt should include:
1. **Subject** - Who or what
2. **Composition** - How it's framed
3. **Action** - What's happening
4. **Location** - Where
5. **Style** - Aesthetic

**Example:**
```
Create a cinematic portrait of a jazz musician [subject] 
playing saxophone [action] on a rainy Paris street [location], 
shot from a low angle [composition]. The style is realistic 
with moody blue and orange lighting [style].
```

### DO's ✅

- Use natural, full-sentence descriptions
- Be specific about camera angles, lighting, lenses
- Use "MUST" and "NEVER" for strict constraints
- Limit text to 1-3 elements per image
- Include negative constraints ("no text", "no watermarks")
- Use reference images for consistency
- Specify aspect ratios for your use case

### DON'Ts ❌

- Use keyword soup ("beautiful amazing stunning")
- Request conflicting styles (photorealistic + cartoon)
- Expect perfect small text rendering
- Use 500+ word prompts
- Be vague about technical specs

### Common Pitfalls

**Vague descriptions:**
❌ "A picture of a cat"
✅ "A tabby cat lounging in a sunlit window, warm afternoon light, cozy home interior"

**Conflicting styles:**
❌ "Photorealistic cartoon character"
✅ "Cartoon character in Pixar 3D animation style"

**Text overload:**
❌ "Poster with title, subtitle, 5 bullet points, footer text"
✅ "Minimalist poster with bold headline only"

## 💡 Examples

### Logo Generation

```bash
uv run scripts/generate_image.py \
  -p "Clean black-and-white logo with text 'Daily Grind', sans-serif font, coffee bean icon, minimalist style" \
  -f logo.png \
  --aspect 1:1 \
  --smart
```

### Product Photography

```bash
uv run scripts/generate_image.py \
  -p "Studio-lit wireless earbuds on polished concrete, 3-point softbox lighting, 45-degree angle, professional e-commerce style" \
  -f product.png \
  --aspect 4:3 \
  --resolution 4K
```

### Character Consistency

```bash
# Step 1: Create base character
uv run scripts/generate_image.py \
  -p "Character reference: young wizard with blue robes, silver staff, friendly smile" \
  -f wizard_ref.png \
  --aspect 1:1

# Step 2: Use as reference for scenes
uv run scripts/generate_image.py \
  -p "The wizard casting a spell in an ancient library" \
  -f wizard_library.png \
  -i wizard_ref.png \
  --aspect 16:9
```

### Social Media Content

```bash
uv run scripts/generate_image.py \
  -p "Instagram story: bold text 'New Collection' at top, fashion model in center, website at bottom, high contrast" \
  -f story.png \
  --aspect 9:16 \
  --smart
```

## 📖 API Reference

### generate_image.py

**Required Arguments:**
- `--prompt, -p`: Image description/prompt
- `--filename, -f`: Output filename

**Optional Arguments:**
- `--input-image, -i`: Input image(s) for editing (can specify multiple)
- `--resolution, -r`: Output resolution (1K, 2K, 4K) - default: 1K
- `--aspect, -a`: Aspect ratio (1:1, 16:9, 9:16, etc.)
- `--smart`: Auto-detect optimal settings
- `--system, -s`: System prompt for consistent constraints
- `--search`: Enable Google Search grounding
- `--template`: Use predefined template
- `--template-var`: Template variables (KEY=VALUE)
- `--validate`: Enable prompt validation (default: True)
- `--no-validate`: Disable validation
- `--api-key, -k`: Gemini API key

### chat_image.py

Interactive mode with no required arguments. Set `GEMINI_API_KEY` environment variable.

**Commands:**
- Type prompts naturally for generation
- `/save <filename>` - Save image
- `/aspect <ratio>` - Change aspect ratio
- `/resolution <size>` - Change resolution
- `/search` - Toggle search grounding
- `/clear` - Clear history
- `/config` - Show settings
- `/help` - Show help
- `exit` or `quit` - Exit

## 🔑 Getting an API Key

1. Visit [Google AI Studio](https://aistudio.google.com/)
2. Create an account or sign in
3. Go to API Keys section
4. Create a new API key
5. Set the environment variable:
   ```bash
   export GEMINI_API_KEY="your-api-key-here"
   ```

## 💰 Pricing

| Resolution | Cost per Image | Best For |
|------------|----------------|----------|
| 1K | ~$0.13 | Web, social media, quick iterations |
| 2K | ~$0.14 | Digital displays, presentations |
| 4K | ~$0.24 | Print materials, large displays |

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built on [Google's Gemini 3 Pro Image API](https://ai.google.dev/)
- Inspired by the Nano Banana Pro model
- Thanks to the Google AI team for the amazing image generation capabilities

## 📞 Support

- Create an [issue](https://github.com/nerveband/nb-pro-image-gen-skill/issues) for bug reports
- Start a [discussion](https://github.com/nerveband/nb-pro-image-gen-skill/discussions) for questions

---

**Happy generating! 🎨✨**
