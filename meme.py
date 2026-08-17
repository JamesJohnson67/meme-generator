from flask import Flask, request, send_file, render_template_string
from PIL import Image, ImageDraw, ImageFont
import io
import textwrap

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Meme Generator</title>
    <style>
        body {
            background: #181818;
            color: white;
            font-family: Arial;
            text-align: center;
            padding: 40px;
        }

        .box {
            max-width: 500px;
            margin: auto;
            background: #292929;
            padding: 30px;
            border-radius: 15px;
        }

        input {
            width: 90%;
            padding: 14px;
            margin: 10px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
        }

        button {
            background: #4caf50;
            color: white;
            border: none;
            padding: 14px 30px;
            border-radius: 8px;
            font-size: 17px;
            cursor: pointer;
            margin-top: 10px;
        }

        button:hover {
            background: #45a049;
        }
    </style>
</head>

<body>
<div class="box">
    <h1>😂 Meme Generator</h1>

    <form action="/generate" method="POST" enctype="multipart/form-data">

        <input
            type="file"
            name="image"
            accept="image/*"
            required
        >

        <input
            type="text"
            name="top_text"
            placeholder="Top text"
        >

        <input
            type="text"
            name="bottom_text"
            placeholder="Bottom text"
        >

        <br>

        <button type="submit">
            Make Meme
        </button>

    </form>
</div>
</body>
</html>
"""


def get_font(size):
    fonts = [
        "arialbd.ttf",
        "Arial Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    ]

    for font in fonts:
        try:
            return ImageFont.truetype(font, size)
        except:
            pass

    return ImageFont.load_default()


def fit_image(image, width=800):
    """
    Automatically resize the image while keeping
    its original aspect ratio.
    """

    image = image.convert("RGB")

    original_width, original_height = image.size

    ratio = width / original_width
    height = int(original_height * ratio)

    return image.resize(
        (width, height),
        Image.Resampling.LANCZOS
    )


def draw_text(draw, text, width, y, font):
    if not text.strip():
        return

    # Wrap long text
    lines = textwrap.wrap(
        text.upper(),
        width=20
    )

    line_height = font.size + 10

    for i, line in enumerate(lines):

        box = draw.textbbox(
            (0, 0),
            line,
            font=font
        )

        text_width = box[2] - box[0]

        x = (width - text_width) // 2

        draw.text(
            (x, y + i * line_height),
            line,
            font=font,
            fill="white",
            stroke_width=max(3, font.size // 15),
            stroke_fill="black"
        )


@app.route("/")
def home():
    return render_template_string(HTML)


@app.route("/generate", methods=["POST"])
def generate():

    uploaded = request.files.get("image")

    if not uploaded:
        return "No image uploaded.", 400

    top_text = request.form.get("top_text", "")
    bottom_text = request.form.get("bottom_text", "")

    try:
        image = Image.open(uploaded)

        # Automatically resize image
        image = fit_image(image, 800)

        width, height = image.size

        draw = ImageDraw.Draw(image)

        # Automatically choose text size
        font_size = max(35, min(90, width // 10))

        font = get_font(font_size)

        # TOP TEXT
        draw_text(
            draw,
            top_text,
            width,
            20,
            font
        )

        # BOTTOM TEXT
        if bottom_text:

            lines = textwrap.wrap(
                bottom_text.upper(),
                width=20
            )

            line_height = font.size + 10

            bottom_height = len(lines) * line_height

            bottom_y = height - bottom_height - 30

            draw_text(
                draw,
                bottom_text,
                width,
                bottom_y,
                font
            )

        # Convert image to memory
        output = io.BytesIO()

        image.save(
            output,
            format="PNG"
        )

        output.seek(0)

        # Open image in browser
        return send_file(
            output,
            mimetype="image/png",
            download_name="meme.png"
        )

    except Exception as e:
        return f"Error: {e}", 500


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )
