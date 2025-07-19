import os
from playwright.async_api import async_playwright
from utils.logger import logger


async def html_to_pdf(html_file_path: str, pdf_file_path: str) -> bool:
    """
    Convert HTML file to PDF using Playwright.
    
    Args:
        html_file_path (str): Path to the HTML file
        pdf_file_path (str): Path for the output PDF file
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        async with async_playwright() as p:
            # Launch browser
            browser = await p.chromium.launch()
            page = await browser.new_page()
            
            # Convert file path to file URL
            file_url = f"file://{os.path.abspath(html_file_path)}"
            
            # Navigate to the HTML file
            await page.goto(file_url)
            
            # Wait for content to load
            await page.wait_for_load_state('networkidle')
            
            # Generate PDF with RTL support and better page break handling
            await page.pdf(
                path=pdf_file_path,
                format='A4',
                print_background=True,
                prefer_css_page_size=True
            )
            
            await browser.close()
        
        logger.info(f"✅ Successfully converted HTML to PDF: {pdf_file_path}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error converting HTML to PDF: {e}")
        return False
    

async def convert_html_to_image(html_file_path: str, image_file_path: str) -> bool:
    """
    Convert HTML file to image using Playwright.
    
    Args:
        html_file_path (str): Path to the HTML file
        image_file_path (str): Path for the output image file
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        async with async_playwright() as p:
            # Launch browser
            browser = await p.chromium.launch()
            page = await browser.new_page()
            
            # Convert file path to file URL
            file_url = f"file://{os.path.abspath(html_file_path)}"
            
            # Navigate to the HTML file
            await page.goto(file_url)
            
            # Wait for content to load
            await page.wait_for_load_state('networkidle')
            
            # Generate image
            await page.screenshot(
                path=image_file_path,
                full_page=True
            )
            
            await browser.close()
        
        logger.info(f"✅ Successfully converted HTML to PDF: {image_file_path}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error converting HTML to PDF: {e}")
        return False