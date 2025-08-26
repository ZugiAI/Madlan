# Madlan Property Search - Installation Guide

This guide will help you set up the Madlan Property Search system on your computer. No technical knowledge required!

## Step 1: Save the Files

1. Download the **Madlan** folder 
2. Save it to your **Desktop**
3. Make sure the folder contains these files:
   - `install.py`
   - `src/mcp_server.py` 
   - `100 listings haifa.xlsx`

## Step 2: Open Terminal/Command Prompt

### On Mac:
1. Press `Command + Space` to open Spotlight
2. Type "Terminal" and press Enter
3. A black window will open - this is the Terminal

### On Windows:
1. Press `Windows key + R`
2. Type "cmd" and press Enter
3. A black window will open - this is the Command Prompt

## Step 3: Navigate to the Madlan Folder

In the Terminal/Command Prompt window, type these commands:

**On Mac:**
```
cd Desktop/Madlan
```

**On Windows:**
```
cd Desktop\Madlan
```

Then press Enter.

## Step 4: Run the Installation

Type this command and press Enter:

```
python3 install.py
```

**Note for Windows users:** If `python3` doesn't work, try:
```
python install.py
```

## Step 5: Wait for Installation to Complete

The installer will automatically:

1. **Check Python installation** - If you don't have Python, it will help you install it
2. **Install required dependencies** - Downloads all necessary software components
3. **Process Excel data** - Converts your property data with precise GPS coordinates
4. **Add transaction classification** - Categorizes properties as "For Sale" vs "To Let"
5. **Create MCP server structure** - Sets up the technical components
6. **Generate configuration guide** - Creates instructions for connecting to Claude Desktop

The installation process may take **10-15 minutes** as it downloads data and processes property locations.

## What You'll See

During installation, you'll see messages like:
- "Creating virtual environment..."
- "Installing packages..."
- "Geocoding addresses..."
- "Processing Excel data..."

This is normal! The system is working.

## After Installation

When complete, you'll see:
- "ENHANCED INSTALLATION COMPLETE!"
- A new `README.md` file with Claude Desktop setup instructions

## Next Steps

1. Open the new `README.md` file
2. Follow the Claude Desktop configuration steps
3. Start searching properties!

## Need Help?

If you see any error messages:
- Make sure the Madlan folder is on your Desktop
- Check that `100 listings haifa.xlsx` is in the folder
- Try closing Terminal/Command Prompt and starting over

The system will guide you through any Python installation if needed.