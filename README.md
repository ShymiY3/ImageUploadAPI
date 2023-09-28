# ImageUploadAPI (Recruitment Task)

## Description
ImageUploadAPI is a Python 3.10 project built primarily using the following packages and frameworks:
- Django
- Django Rest Framework
- Pillow

### Overview
ImageUploadAPI is an API that allows users to upload and manage images. It offers additional features such as user tiers and their capabilities. Some of the key functionalities include:
- Uploading images
- Generating thumbnails
- Creating expiring image links
- Admin capabilities to build user tiers with various modifications, such as storing original images and generating different thumbnail sizes, and enabling the creation of expiring links.

## Getting Started
To set up the project, follow these steps:

1. Clone the repository: `git clone https://github.com/ShymiY3/ImageUploadAPI.git`
2. Navigate to the project directory.
3. Modify `.env` file to update the secret key.
4. Build and run the project using Docker Compose: `docker-compose up`
5. Initialize the admin panel by running: `docker-compose run python manage.py runserver`
