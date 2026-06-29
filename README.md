# SnapVault — Family Memories

SnapVault is a web application built with Flask designed to securely store, organize, and manage family memories. It features a highly polished, immersive, and interactive user interface that elevates the photo-viewing experience.

## Features

- **User Authentication**: Secure login and session management.
- **Image Management**: Upload, delete, and update image metadata (description, date, tags, favorites).
- **Cloud Storage Integration**: Seamlessly upload images to Cloudinary.
- **Cloudinary Sync**: Automatically sync images from your Cloudinary `family_vault` folder.
- **Search & Filter**: Search images by description or tags, and filter by category or favorites.
- **Export**: Export image metadata as a ZIP archive.

## UI/UX & Design Theme

The application is styled with a premium **"Frost/Winter" aesthetics** and **Glassmorphism**, aiming to create a highly immersive, magical, and premium gallery experience.

### Core Design Elements:
- **Glassmorphism Panels**: UI components use deep frosted glass effects (`backdrop-filter: blur`), semi-transparent dark backgrounds, and subtle luminous borders to create depth against the dynamic background.
- **Dynamic Backgrounds**: 
  - Smooth **Aurora** animations that blend deep blues and frosty cyans across the viewport.
  - Interactive **Snowflakes** falling gracefully.
  - Floating glowing orbs (**Fireflies**) adding a magical touch.
- **Typography**: 
  - **Inter** (sans-serif) for clean, readable body text.
  - **Noto Serif JP** for elegant, high-impact headings and brand text.
- **Color Palette**:
  - **Frost Blues**: Base `#89CFF0`, Light `#B0E0E6`, Dark `#4682B4` used for accents, text gradients, and glowing effects.
  - **Ink Dark**: `#0A0A10` for deep, rich dark backgrounds emphasizing the glowing elements.
- **Animations & Micro-interactions**:
  - Shimmering frost text gradients (`frost-text`).
  - Animated glowing buttons (`btn-frost`) with sweep shine effects on hover.
  - Image cards scale and rotate slightly on hover, revealing gradient overlays.
- **Tailwind CSS & FontAwesome**: Rapid layout structuring and crisp iconography.

## Tech Stack

- **Backend**: Python, Flask, Flask-SQLAlchemy, Flask-Login, Flask-WTF
- **Database**: SQLite
- **Cloud Storage**: Cloudinary API
- **Frontend**: HTML, Vanilla CSS (with Custom Animations), Tailwind CSS (via CDN), JavaScript

## Prerequisites

- Python 3.x
- Cloudinary Account (if you plan to change the default configuration)

## Installation

1. **Clone the repository:**
   ```bash
   # navigate to your preferred directory
   cd gallery-memories-main
   ```

2. **Install dependencies:**
   It is recommended to use a virtual environment.
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Variables:**
   Create a `.env` file in the root directory to store your secret keys:
   ```env
   SECRET_KEY=your_flask_secret_key
   ```
   *Note: Cloudinary credentials are currently configured directly in `app.py`. For better security, consider moving them to this `.env` file.*

4. **Run the application:**
   ```bash
   python app.py
   ```
   The application will start running at `http://localhost:5000`.

## Default Credentials

Upon running the application for the first time, a default user is created automatically:
- **Username**: nishanth
- **Password**: knh@2005

*Please ensure you change these credentials or disable this feature in a production environment.*

## Deployment

This app includes a `vercel.json` configuration file, making it ready for deployment on Vercel. 
Note: When deploying on Vercel, the app is configured to use a temporary SQLite database (`/tmp/snapvault.db`). For persistent storage in a production environment, you should connect to a remote database like PostgreSQL.
