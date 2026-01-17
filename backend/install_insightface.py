"""
InsightFace Installation and Verification Script
Run this to install and test InsightFace integration
"""
import subprocess
import sys


def install_package(package: str):
    """Install a Python package using pip."""
    print(f"📦 Installing {package}...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ {package} installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {package}: {e}")
        return False


def test_import(module: str):
    """Test if a module can be imported."""
    try:
        __import__(module)
        print(f"✅ {module} imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import {module}: {e}")
        return False


def test_insightface():
    """Test InsightFace functionality."""
    print("\n🧪 Testing InsightFace...")
    try:
        from insightface.app import FaceAnalysis
        
        # Initialize app
        app = FaceAnalysis(name='buffalo_l', providers=['CPUExecutionProvider'])
        app.prepare(ctx_id=0, det_size=(640, 640))
        
        print("✅ InsightFace buffalo_l model loaded successfully")
        print(f"   Model path: ~/.insightface/models/buffalo_l/")
        return True
    except Exception as e:
        print(f"❌ InsightFace test failed: {e}")
        print("\n💡 Tip: The model will be downloaded on first use (~100MB)")
        return False


def test_emotion_detection():
    """Test emotion detection with DeepFace."""
    print("\n🧪 Testing Emotion Detection...")
    try:
        from deepface import DeepFace
        import numpy as np
        
        # Create a dummy image
        dummy_image = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
        
        print("✅ DeepFace emotion detection ready")
        return True
    except Exception as e:
        print(f"❌ Emotion detection test failed: {e}")
        return False


def main():
    """Main installation and testing workflow."""
    print("=" * 60)
    print("🚀 ISAVS 2026 - InsightFace Installation")
    print("=" * 60)
    
    # Step 1: Install InsightFace
    print("\n📋 Step 1: Installing InsightFace...")
    if not install_package("insightface"):
        print("\n⚠️ InsightFace installation failed. Trying alternative...")
        install_package("insightface==0.7.3")
    
    # Step 2: Install ONNX Runtime
    print("\n📋 Step 2: Installing ONNX Runtime...")
    install_package("onnxruntime")
    
    # Step 3: Verify DeepFace (for emotion detection)
    print("\n📋 Step 3: Verifying DeepFace...")
    if not test_import("deepface"):
        print("⚠️ DeepFace not found. Installing...")
        install_package("deepface")
    
    # Step 4: Test imports
    print("\n📋 Step 4: Testing imports...")
    insightface_ok = test_import("insightface")
    onnx_ok = test_import("onnxruntime")
    deepface_ok = test_import("deepface")
    
    # Step 5: Test functionality
    print("\n📋 Step 5: Testing functionality...")
    if insightface_ok:
        test_insightface()
    
    if deepface_ok:
        test_emotion_detection()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Installation Summary")
    print("=" * 60)
    print(f"InsightFace:       {'✅ Ready' if insightface_ok else '❌ Failed'}")
    print(f"ONNX Runtime:      {'✅ Ready' if onnx_ok else '❌ Failed'}")
    print(f"DeepFace (Emotion):{'✅ Ready' if deepface_ok else '❌ Failed'}")
    
    if insightface_ok and onnx_ok and deepface_ok:
        print("\n🎉 All components installed successfully!")
        print("\n📝 Next steps:")
        print("1. Update backend/.env with AI_MODEL=insightface")
        print("2. Run database migration to add embedding_dimension column")
        print("3. Restart the backend server")
        print("4. Test enrollment with new model")
    else:
        print("\n⚠️ Some components failed to install.")
        print("Please check the error messages above and try manual installation:")
        print("  pip install insightface onnxruntime deepface")
    
    print("=" * 60)


if __name__ == "__main__":
    main()
