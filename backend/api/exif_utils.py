from PIL import Image
import exifread
from io import BytesIO

def extract_exif(image_file):
    """
    提取EXIF信息，返回dict
    """
    image_file.seek(0)
    tags = exifread.process_file(image_file, details=False)
    exif_data = {}
    for tag, value in tags.items():
        exif_data[tag] = str(value)
    return exif_data

def get_datetime_location(exif_data):
    """
    从EXIF中提取拍摄时间和GPS信息
    """
    dt = exif_data.get('EXIF DateTimeOriginal') or exif_data.get('Image DateTime')
    gps_lat = exif_data.get('GPS GPSLatitude')
    gps_lat_ref = exif_data.get('GPS GPSLatitudeRef')
    gps_lon = exif_data.get('GPS GPSLongitude')
    gps_lon_ref = exif_data.get('GPS GPSLongitudeRef')
    def _convert_gps(coord, ref):
        if not coord or not ref:
            return None
        # exifread的值通常为字符串，需解析
        try:
            parts = [float(x) for x in str(coord).replace('[','').replace(']','').split(',')]
            decimal = parts[0] + parts[1]/60 + parts[2]/3600
            if ref in ['S', 'W']:
                decimal = -decimal
            return decimal
        except Exception:
            return None
    lat = _convert_gps(gps_lat, gps_lat_ref) if gps_lat and gps_lat_ref else None
    lon = _convert_gps(gps_lon, gps_lon_ref) if gps_lon and gps_lon_ref else None
    return dt, lat, lon

def generate_thumbnail(image_file, size=(256, 256)):
    """
    生成缩略图，返回BytesIO对象
    """
    image_file.seek(0)
    img = Image.open(image_file)
    img.thumbnail(size)
    thumb_io = BytesIO()
    img.save(thumb_io, format=img.format or 'JPEG')
    thumb_io.seek(0)
    return thumb_io
