import logging
import urllib.request
import tempfile
import os
from io import BytesIO
from PIL import Image, ImageOps
import cloudinary.uploader

def fetch_image_as_jpeg(url, target_size=None):
    if url.lower().endswith('.pdf'):
        url = url[:-4] + '.jpg'

    req = urllib.request.urlopen(url)
    img = Image.open(BytesIO(req.read()))
    if img.mode in ("RGBA", "P"):
        if img.mode == "RGBA":
            bg = Image.new("RGB", img.size, (255, 255, 255))
            bg.paste(img, mask=img.split()[3])
            img = bg
        else:
            img = img.convert("RGB")
        
    if target_size:
        img = ImageOps.exif_transpose(img)
        
        # Auto-crop signatures (target aspect ratio > 1)
        if target_size[0] > target_size[1]:
            try:
                from PIL import ImageFilter
                gray = img.convert('L')
                w, h = img.size
                bx, by = int(w*0.02), int(h*0.02)
                edges = gray.filter(ImageFilter.FIND_EDGES).crop((bx, by, w-bx, h-by))
                max_edge = edges.getextrema()[1]
                threshold = max(20, int(max_edge * 0.2))
                bw = edges.point(lambda x: 255 if x > threshold else 0, '1')
                bbox = bw.getbbox()
                if bbox:
                    l, t, r, b = bbox
                    l += bx; t += by; r += bx; b += by
                    pad_x = int((r-l)*0.05)
                    pad_y = int((b-t)*0.05)
                    img = img.crop((max(0, l-pad_x), max(0, t-pad_y), min(w, r+pad_x), min(h, b+pad_y)))
            except Exception as e:
                logging.error(f"Auto-crop failed: {e}")
                
        img = ImageOps.contain(img, target_size, Image.Resampling.LANCZOS if hasattr(Image, 'Resampling') else Image.ANTIALIAS)
        
    fd, path = tempfile.mkstemp(suffix=".jpg")
    os.close(fd)
    img.save(path, format="JPEG")
    return path

def upload_to_cloudinary(file_obj, folder_name):
    """Upload file directly to Cloudinary and return secure URL."""
    if not file_obj or file_obj.filename == '':
        return None
    try:
        res = cloudinary.uploader.upload(file_obj, folder=folder_name, resource_type="image")
        return res.get("secure_url")
    except Exception as e:
        logging.error(f"Cloudinary upload failed: {e}")
        return None
