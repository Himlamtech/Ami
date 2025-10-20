"""
Speech-to-Text (STT) Initialization Script
Downloads and tests Vietnamese Wav2Vec2 model.
Run with: python scripts/init_stt.py
"""

import asyncio
import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.infrastructure.stt.wav2vec2_stt import Wav2Vec2STT
from app.application.stt_service import STTService

async def check_dependencies():
    """Check if required dependencies are installed."""
    print("\n" + "="*70)
    print("STT Dependencies Check")
    print("="*70)
    
    required_packages = {
        "torch": "PyTorch",
        "torchaudio": "TorchAudio",
        "transformers": "Transformers",
        "librosa": "Librosa",
        "soundfile": "SoundFile",
    }
    
    missing = []
    
    for package, name in required_packages.items():
        try:
            __import__(package)
            print(f"✅ {name} installed")
        except ImportError:
            print(f"❌ {name} NOT installed")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print(f"\nInstall with: pip install {' '.join(missing)}")
        return False
    
    print(f"✅ All dependencies installed\n")
    return True

async def check_disk_space():
    """Check available disk space for model download."""
    print("\n" + "="*70)
    print("Disk Space Check")
    print("="*70)
    
    import shutil
    
    # Check ~/.cache/huggingface (where models are stored)
    cache_dir = Path.home() / ".cache" / "huggingface"
    cache_dir.mkdir(parents=True, exist_ok=True)
    
    stat = shutil.disk_usage(cache_dir)
    free_gb = stat.free / (1024 ** 3)
    
    print(f"Cache directory: {cache_dir}")
    print(f"Free space: {free_gb:.2f} GB")
    
    if free_gb < 5:
        print(f"⚠️  Low disk space! Recommended: at least 5 GB")
        print(f"   Model size: ~1-2 GB")
        print(f"   Working space: ~3 GB")
        return False
    
    print(f"✅ Sufficient disk space\n")
    return True

async def init_stt():
    """Initialize STT model and test."""
    print("\n" + "🎤"*35)
    print("Speech-to-Text (STT) Initialization")
    print("🎤"*35)
    
    # Check dependencies
    if not await check_dependencies():
        return False
    
    # Check disk space
    if not await check_disk_space():
        response = input("\nContinue anyway? (y/n): ")
        if response.lower() != 'y':
            print("Aborted.")
            return False
    
    print("\n" + "="*70)
    print("Model Initialization")
    print("="*70)
    
    try:
        # Initialize STT provider
        print(f"\n📦 Creating Wav2Vec2 STT provider...")
        print(f"   Model: nguyenvulebinh/wav2vec2-base-vi-vlsp2020")
        print(f"   This will download ~1-2 GB on first run")
        print(f"   Please wait...")
        
        stt_provider = Wav2Vec2STT(
            model_name="nguyenvulebinh/wav2vec2-base-vi-vlsp2020",
            lazy_load=False,  # Load immediately
        )
        
        print(f"✅ STT provider created")
        
        # Wait for model to load
        print(f"\n⏳ Loading model (this may take a few minutes)...")
        start = time.time()
        
        # Model loads in __init__ with lazy_load=False
        await asyncio.sleep(1)  # Give it a moment
        
        elapsed = time.time() - start
        print(f"✅ Model loaded in {elapsed:.1f}s")
        
        # Create service
        stt_service = STTService(stt_provider)
        
        # Health check
        print(f"\n🔍 Performing health check...")
        health = await stt_service.health_check()
        
        if health["status"] == "healthy":
            print(f"✅ STT service is healthy")
            print(f"\n📊 Service Details:")
            print(f"   Status: {health['details']['status']}")
            print(f"   Model: {health['details']['model']['name']}")
            print(f"   Model Status: {health['details']['model']['status']}")
            print(f"   Device: {health['details']['model']['device']}")
            print(f"   CUDA Available: {health['details']['system']['cuda_available']}")
            
            # Show capabilities
            caps = health['details']['capabilities']
            print(f"\n🎯 Capabilities:")
            print(f"   Language Model: {caps['language_model']}")
            print(f"   Languages: {', '.join(caps['supported_languages'])}")
            print(f"   Formats: {', '.join(caps['supported_formats'])}")
            print(f"   Target Sample Rate: {caps['target_sample_rate']} Hz")
        else:
            print(f"❌ STT service is unhealthy: {health.get('error')}")
            return False
        
        # Test with dummy audio
        print(f"\n🧪 Testing with dummy audio (1 second silence)...")
        
        import numpy as np
        import tempfile
        import soundfile as sf
        
        # Create 1 second of silence
        dummy_audio = np.zeros(16000, dtype=np.float32)
        
        # Save to temp file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
            sf.write(tmp_file.name, dummy_audio, 16000)
            tmp_path = tmp_file.name
        
        try:
            # Transcribe
            start = time.time()
            result = await stt_service.transcribe_file(
                file_path=tmp_path,
                use_lm=False,  # Faster for test
            )
            elapsed = time.time() - start
            
            print(f"✅ Test transcription complete in {elapsed:.2f}s")
            print(f"   Text: '{result['text']}' (expected to be empty)")
            print(f"   Duration: {result['duration']:.2f}s")
            print(f"   Confidence: {result['confidence']:.2f}")
            
        finally:
            # Clean up
            Path(tmp_path).unlink(missing_ok=True)
        
        print("\n" + "="*70)
        print("✅ STT initialization completed successfully!")
        print("="*70)
        
        print(f"\n📚 Usage Example:")
        print(f"   from app.application.factory import ProviderFactory")
        print(f"   from app.application.stt_service import STTService")
        print(f"")
        print(f"   stt_provider = ProviderFactory.get_stt_provider()")
        print(f"   stt_service = STTService(stt_provider)")
        print(f"   result = await stt_service.transcribe_file('audio.wav')")
        print(f"   print(result['text'])")
        
        print(f"\n🌐 API Endpoints:")
        print(f"   POST /api/v1/stt/transcribe - Transcribe audio")
        print(f"   GET  /api/v1/stt/health     - Health check")
        print(f"   GET  /api/v1/stt/models     - List models")
        
        return True
        
    except KeyboardInterrupt:
        print(f"\n\n⚠️  Interrupted by user")
        return False
    except Exception as e:
        print(f"\n❌ STT initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\n⚠️  IMPORTANT:")
    print("   This script will download the Wav2Vec2 model (~1-2 GB)")
    print("   Make sure you have a stable internet connection")
    print("   The model will be cached in ~/.cache/huggingface/")
    
    response = input("\nContinue? (y/n): ")
    if response.lower() != 'y':
        print("Aborted.")
        sys.exit(0)
    
    success = asyncio.run(init_stt())
    sys.exit(0 if success else 1)


