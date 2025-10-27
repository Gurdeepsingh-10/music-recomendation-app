import requests
import zipfile
import os
from pathlib import Path

def download_fma_metadata():
    """Download Free Music Archive metadata"""
    
    data_dir = Path(__file__).parent.parent / "data"
    data_dir.mkdir(exist_ok=True)
    
    url = "https://os.unil.cloud.switch.ch/fma/fma_metadata.zip"
    zip_path = data_dir / "fma_metadata.zip"
    
    print("📥 Downloading FMA metadata (342 MB)...")
    print("⏳ This may take 5-10 minutes depending on your internet speed...")
    
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    
    with open(zip_path, 'wb') as f:
        downloaded = 0
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
            downloaded += len(chunk)
            if total_size:
                percent = (downloaded / total_size) * 100
                print(f"  Progress: {percent:.1f}%", end='\r')
    
    print("\n✅ Download complete!")
    print("📦 Extracting files...")
    
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(data_dir)
    
    print("✅ Extraction complete!")
    print(f"📁 Files saved to: {data_dir / 'fma_metadata'}")
    
    # Clean up zip file
    os.remove(zip_path)
    print("🧹 Cleaned up zip file")

if __name__ == "__main__":
    download_fma_metadata()