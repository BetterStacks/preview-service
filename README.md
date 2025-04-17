# preview-service

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Travis](https://img.shields.io/travis/FPurchess/preview-service/master.svg?logo=travis)](https://travis-ci.org/FPurchess/preview-service)

Super slim webservice to generate thumbnail images for document files (pdf, odt, doc, docx), video files (mp4, flv, webm, ogv, wmv), 3D Files (ply, obj, stl) and many more using a simple HTTP API.

This is a simple wrapper around [algoo/preview-generator](https://github.com/algoo/preview-generator).

See the [full list of supported file formats](https://github.com/algoo/preview-generator#supported-file-formats).

## Usage

### Using Docker Hub Image

Boot up the service using the pre-built Docker image:

```bash
docker run -p 8000:8000 fpurchess/preview-service
```

### Local Development with Docker Compose

For local development or building from source:

```bash
# Build and start the service
docker-compose up --build

# Run in detached mode
docker-compose up -d
```

### Creating Thumbnails

Use the service to create a thumbnail:

```bash
# Using a local file
curl -o thumbnail.jpeg -F 'file=file_to_preview.pdf' http://localhost:8000/preview/100x100

# Using a URL (signed S3 URL, etc.)
curl -o thumbnail.jpeg -F 'file_url=https://example.com/file_to_preview.pdf' http://localhost:8000/preview/100x100
```

## Optional Volumes

- `/tmp/cache/` - mount it to persist thumbnail cache
- `/tmp/files/` - stores all uploaded files

Here's a full example:

```bash
docker run -p 8000:8000 -v /tmp/cache/:/tmp/cache/ -v /tmp/files/:/tmp/files/ fpurchess/preview-service
```

## API

### GET `/`

Returns 200 OK when the service is up and running.

### POST `/preview/{width}x{height}`

Accepts one of the following in a `multipart/form-data`:
- A file to be converted with form name `file`
- A URL pointing to a file with form name `file_url` (e.g., a signed S3 URL)

Returns the converted file as a file response if the conversion is successful.

```bash
# Using a local file
curl -o thumbnail.jpeg -F 'file=file_to_preview.pdf' http://localhost:8000/preview/100x100

# Using a URL
curl -o thumbnail.jpeg -F 'file_url=https://example.com/file_to_preview.pdf' http://localhost:8000/preview/100x100

# For video files
curl -o thumbnail.jpeg -F 'file=video.mp4' http://localhost:8000/preview/320x180
```

Creates a JPEG thumbnail image of the provided file with the specified dimensions and stores it in the output file.

#### Supported File Types

- **Documents**: PDF, DOC, DOCX, ODT, TXT, RTF, PPT, PPTX
- **Images**: JPG, JPEG, PNG, GIF, BMP, SVG, TIFF, WEBP
- **Videos**: MP4, FLV, WEBM, OGV, WMV, MOV, AVI, M4V, MPG, MPEG
- **Others**: See [full list of supported formats](https://github.com/algoo/preview-generator#supported-file-formats)

### GET `/cache/<cached-file>`

Returns a cached converted file if present.

## Thanks

Thanks [algoo](https://github.com/algoo/) and all contributors of [algoo/preview-generator](https://github.com/algoo/preview-generator).

## LICENSE

see LICENSE file
