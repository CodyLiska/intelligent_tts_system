# Left off at
- ~~Just added: systhesize.py, align_subtitles.py, make_captions.py, but they have errors.~~
- [ ] need to make sure cacheing works 
- [ ] optimize time to produce audio
- [ ] test again with temlpate curl commands
- [ ] have ai review the complete project in a zip file


## Plan to continue
1. Testing on Windows side is complete, works perfect using Kokoro and will never use CosyVoice2.
2. Need to test on MacBook Pro to see how CosyVoice2 works.


# CURL COMMANDS for TESTING

### v1

#### Kokoro (GET) ✅
- curl.exe -Ns "http://127.0.0.1:8000/synthesize/stream_get?engine=kokoro&voice=af_heart&max_chars=100&text=Hello%20from%20the%20GET%20stream" | ffplay -autoexit -nodisp -fflags nobuffer -flags low_delay -probesize 32 -analyzeduration 0 -i pipe:0

#### CosyVoice2 (preset ref id)
- curl.exe -Ns "http://127.0.0.1:8000/synthesize/stream_get?engine=cosyvoice2&cosy_mode=cross&cosy_ref_id=ref&max_chars=60&speed=1.15&text=Remote%20reference%20test" | ffplay -autoexit -nodisp -fflags nobuffer -flags low_delay -probesize 32 -analyzeduration 0 -i pipe:0

#### CosyVoice2 (remote ref URL)
- $ref = [uri]::EscapeDataString("https://samplelib.com/lib/preview/wav/sample-3s.wav")
- curl.exe -Ns "http://127.0.0.1:8000/synthesize/stream_get?engine=cosyvoice2&cosy_mode=cross&cosy_ref_url=$ref&max_chars=60&speed=1.15&text=Remote%20reference%20test" | ffplay -autoexit -nodisp -fflags nobuffer -flags low_delay -probesize 32 -analyzeduration 0 -i pipe:0

### v2

#### Kokoro POST (works now; should start instantly) ✅
- curl.exe -s -X POST "http://127.0.0.1:8000/synthesize/stream" -F "text=This is a streaming test." -F "engine=kokoro" -F "voice=af_heart" | ffplay -autoexit -nodisp -i pipe:0

#### Kokoro GET ✅
- curl.exe -Ns "http://127.0.0.1:8000/synthesize/stream_get?engine=kokoro&voice=af_heart&max_chars=100&text=Hello%20from%20the%20GET%20stream" | ffplay -autoexit -nodisp -i pipe:0

#### CosyVoice2 (preset ref id)
- curl.exe -Ns "http://127.0.0.1:8000/synthesize/stream_get?engine=cosyvoice2&cosy_mode=cross&cosy_ref_id=ref&max_chars=60&speed=1.1&text=Remote%20reference%20test" | ffplay -autoexit -nodisp -i pipe:0

#### CosyVoice2 (remote ref URL)
- $ref = [uri]::EscapeDataString("https://samplelib.com/lib/preview/wav/sample-3s.wav")
- curl.exe -Ns "http://127.0.0.1:8000/synthesize/stream_get?engine=cosyvoice2&cosy_mode=cross&cosy_ref_url=$ref&max_chars=60&speed=1.1&text=Remote%20reference%20test" | ffplay -autoexit -nodisp -i pipe:0

# TESTING RESULTS TEMPLATE

## TESTING RESULTS #

### 1. CosyVoice2 (preset ref id)
   - curl.exe -Ns "http://127.0.0.1:8000/synthesize/stream_get?engine=cosyvoice2&cosy_mode=cross&cosy_ref_id=ref&max_chars=60&speed=1.1&text=Remote%20reference%20test" | ffplay -autoexit -nodisp -i pipe:0 
   - Response Time: 
   - Audo Quality: 
   - Output:
     - 
   - Error Details:
     - 

### 2. CosyVoice2 (remote ref URL)
   - $ref = [uri]::EscapeDataString("https://samplelib.com/lib/preview/wav/sample-3s.wav")
   - curl.exe -Ns "http://127.0.0.1:8000/synthesize/stream_get?engine=cosyvoice2&cosy_mode=cross&cosy_ref_url=$ref&max_chars=60&speed=1.1&text=Remote%20reference%20test" | ffplay -autoexit -nodisp -i pipe:0 
   - Response Time: 
   - Audo Quality: 
   - Output:
     - 
   - Error Details:
     - 

### 3. Kokoro — GET *Happy with results, no changes needed*
   - curl.exe -Ns "http://127.0.0.1:8000/synthesize/stream_get?engine=kokoro&voice=af_heart&max_chars=100&text=Hello%20from%20the%20GET%20stream" | ffplay -autoexit -nodisp -i pipe:0 
   - Response Time: 
   - Audo Quality: 
   - Output:
     -  

### 4. Kokoro — POST *Happy with results, no changes needed*
   - curl.exe -s -X POST "http://127.0.0.1:8000/synthesize/stream" -F "text=This is a streaming test." -F "engine=kokoro" -F "voice=af_heart" | ffplay -autoexit -nodisp -i pipe:0 
   - Response Time: 
   - Audo Quality: 
   - Output:
     - 

### 5. PCM — lower latency, no warnings
   - curl.exe -Ns "http://127.0.0.1:8000/synthesize/stream_get?engine=cosyvoice2&cosy_mode=cross&cosy_ref_id=ref&max_chars=60&speed=1.1&fmt=pcm&text=Remote%20reference%20test" | ffplay -autoexit -nodisp -f s16le -ar 24000 -ac 1 -i pipe:0
   - Response Time: 
   - Audo Quality: 
   - Output:
     - 
   - Error Details: 
     - 

### 6. WAV - current default
   - curl.exe -Ns "http://127.0.0.1:8000/synthesize/stream_get?engine=cosyvoice2&cosy_mode=cross&cosy_ref_id=ref&max_chars=60&speed=1.1&text=Remote%20reference%20test" | ffplay -autoexit -nodisp -i pipe:0
   - Response Time: 
   - Audo Quality: 
   - Output:
     - 
   - Error Details:
     - 

### 7. Kokoro - GET (PCM)
   - curl.exe -Ns "http://127.0.0.1:8000/synthesize/stream_get?engine=kokoro&voice=af_heart&max_chars=100&fmt=pcm&text=Hello%20from%20the%20GET%20stream" | ffplay -autoexit -nodisp -f s16le -ar 24000 -i pipe:0
   - Response Time: 
   - Audo Quality: 
   - Output:
     - 
   - Error Details:
    - 

### 8. Kokoro - GET (WAV)  *Happy with results, no changes needed*
   - curl.exe -Ns "http://127.0.0.1:8000/synthesize/stream_get?engine=kokoro&voice=af_heart&max_chars=100&text=Hello%20from%20the%20GET%20stream" | ffplay -autoexit -nodisp -i pipe:0
   - Response Time: 
   - Audo Quality: Prfect
   - Output:
     - 

### 9. Kokoro — POST (your fast path) [PCM]  *Happy with results, no changes needed*
   - curl.exe -s -X POST "http://127.0.0.1:8000/synthesize/stream" -F "text=This is a streaming test." -F "engine=kokoro" -F "voice=af_heart" -F "fmt=pcm" | ffplay -autoexit -nodisp -f s16le -ar 24000 -ac 1 -i pipe:0
   - Response Time: 
   - Audo Quality: 
   - Output:
     - 

### 10. Kokoro — POST (your fast path) [WAV]  *Happy with results, no changes needed*
   - curl.exe -s -X POST "http://127.0.0.1:8000/synthesize/stream" -F "text=This is a streaming test." -F "engine=kokoro" -F "voice=af_heart" | ffplay -autoexit -nodisp -i pipe:0
   - Response Time: 
   - Audo Quality: 
   - Output:
     - 



# TESTING RESULTS #1

1. curl.exe -Ns "http://127.0.0.1:8000/synthesize/stream_get?engine=cosyvoice2&cosy_mode=cross&cosy_ref_id=ref&max_chars=60&speed=1.1&text=Remote%20reference%20test" | ffplay -autoexit -nodisp -i pipe:0 
   - took 17 seconds and the audio was good 

2. curl.exe -Ns "http://127.0.0.1:8000/synthesize/stream_get?engine=cosyvoice2&cosy_mode=cross&cosy_ref_id=ref&max_chars=60&speed=1.1&text=Remote%20reference%20test" | ffplay -autoexit -nodisp -i pipe:0 
   - took 17 seconds and the audio was good 

3. $ref = [uri]::EscapeDataString("https://samplelib.com/lib/preview/wav/sample-3s.wav")
   curl.exe -Ns "http://127.0.0.1:8000/synthesize/stream_get?engine=cosyvoice2&cosy_mode=cross&cosy_ref_url=$ref&max_chars=60&speed=1.1&text=Remote%20reference%20test" | ffplay -autoexit -nodisp -i pipe:0 
   - took 15 seconds and the audio was very low 

4. curl.exe -Ns "http://127.0.0.1:8000/synthesize/stream_get?engine=kokoro&voice=af_heart&max_chars=100&text=Hello%20from%20the%20GET%20stream" | ffplay -autoexit -nodisp -i pipe:0 
   - took 5 seconds and audio was perfect. not sure if this can be further optimized but let me know. 

5. curl.exe -s -X POST "http://127.0.0.1:8000/synthesize/stream" -F "text=This is a streaming test." -F "engine=kokoro" -F "voice=af_heart" | ffplay -autoexit -nodisp -i pipe:0 
   - took 2.5 seconds and the audio was perfect. also not sure if this can be further optimized but let me know.


# TESTING RESULTS #2

1. curl.exe -Ns "http://127.0.0.1:8000/synthesize/stream_get?engine=cosyvoice2&cosy_mode=cross&cosy_ref_id=ref&max_chars=60&speed=1.1&text=Remote%20reference%20test" | ffplay -autoexit -nodisp -i pipe:0 
   - took about 10 seconds and the audio was good
   - ffplay version 7.1.1-full_build-www.gyan.dev Copyright (c) 2003-2025 the FFmpeg developers
      built with gcc 14.2.0 (Rev1, Built by MSYS2 project)
      configuration: --enable-gpl --enable-version3 --enable-static --disable-w32threads --disable-autodetect --enable-fontconfig --enable-iconv --enable-gnutls --enable-lcms2 --enable-libxml2 --enable-gmp --enable-bzlib --enable-lzma --enable-libsnappy --enable-zlib --enable-librist --enable-libsrt --enable-libssh --enable-libzmq --enable-avisynth --enable-libbluray --enable-libcaca --enable-libdvdnav --enable-libdvdread --enable-sdl2 --enable-libaribb24 --enable-libaribcaption --enable-libdav1d --enable-libdavs2 --enable-libopenjpeg --enable-libquirc --enable-libuavs3d --enable-libxevd --enable-libzvbi --enable-libqrencode --enable-librav1e --enable-libsvtav1 --enable-libvvenc --enable-libwebp --enable-libx264 --enable-libx265 --enable-libxavs2 --enable-libxeve --enable-libxvid --enable-libaom --enable-libjxl --enable-libvpx --enable-mediafoundation --enable-libass --enable-frei0r --enable-libfreetype --enable-libfribidi --enable-libharfbuzz --enable-liblensfun --enable-libvidstab --enable-libvmaf --enable-libzimg --enable-amf --enable-cuda-llvm --enable-cuvid --enable-dxva2 --enable-d3d11va --enable-d3d12va --enable-ffnvcodec --enable-libvpl --enable-nvdec --enable-nvenc --enable-vaapi --enable-libshaderc --enable-vulkan --enable-libplacebo --enable-opencl --enable-libcdio --enable-libgme --enable-libmodplug --enable-libopenmpt --enable-libopencore-amrwb --enable-libmp3lame --enable-libshine --enable-libtheora --enable-libtwolame --enable-libvo-amrwbenc --enable-libcodec2 --enable-libilbc --enable-libgsm --enable-liblc3 --enable-libopencore-amrnb --enable-libopus --enable-libspeex --enable-libvorbis --enable-ladspa --enable-libbs2b --enable-libflite --enable-libmysofa --enable-librubberband --enable-libsoxr --enable-chromaprint
      libavutil      59. 39.100 / 59. 39.100
      libavcodec     61. 19.101 / 61. 19.101
      libavformat    61.  7.100 / 61.  7.100
      libavdevice    61.  3.100 / 61.  3.100
      libavfilter    10.  4.100 / 10.  4.100
      libswscale      8.  3.100 /  8.  3.100
      libswresample   5.  3.100 /  5.  3.100
      libpostproc    58.  3.100 / 58.  3.100
    [wav @ 00000222f6993400] Ignoring maximum wav data size, file may be invalid
    [wav @ 00000222f6993400] Packet corrupt (stream = 0, dts = NOPTS).
    Input #0, wav, from 'pipe:0':
      Duration: N/A, bitrate: 384 kb/s
      Stream #0:0: Audio: pcm_s16le ([1][0][0][0] / 0x0001), 24000 Hz, 1 channels, s16, 384 kb/s
      1.50 M-A:  0.000 fd=   0 aq=    0KB vq=    0KB sq=    0B

2. curl.exe -Ns "http://127.0.0.1:8000/synthesize/stream_get?engine=cosyvoice2&cosy_mode=cross&cosy_ref_id=ref&max_chars=60&speed=1.1&text=Remote%20reference%20test" | ffplay -autoexit -nodisp -i pipe:0 
   - took 13 seconds and the audio was a little muffled
   - ffplay version 7.1.1-full_build-www.gyan.dev Copyright (c) 2003-2025 the FFmpeg developers
      built with gcc 14.2.0 (Rev1, Built by MSYS2 project)
      configuration: --enable-gpl --enable-version3 --enable-static --disable-w32threads --disable-autodetect --enable-fontconfig --enable-iconv --enable-gnutls --enable-lcms2 --enable-libxml2 --enable-gmp --enable-bzlib --enable-lzma --enable-libsnappy --enable-zlib --enable-librist --enable-libsrt --enable-libssh --enable-libzmq --enable-avisynth --enable-libbluray --enable-libcaca --enable-libdvdnav --enable-libdvdread --enable-sdl2 --enable-libaribb24 --enable-libaribcaption --enable-libdav1d --enable-libdavs2 --enable-libopenjpeg --enable-libquirc --enable-libuavs3d --enable-libxevd --enable-libzvbi --enable-libqrencode --enable-librav1e --enable-libsvtav1 --enable-libvvenc --enable-libwebp --enable-libx264 --enable-libx265 --enable-libxavs2 --enable-libxeve --enable-libxvid --enable-libaom --enable-libjxl --enable-libvpx --enable-mediafoundation --enable-libass --enable-frei0r --enable-libfreetype --enable-libfribidi --enable-libharfbuzz --enable-liblensfun --enable-libvidstab --enable-libvmaf --enable-libzimg --enable-amf --enable-cuda-llvm --enable-cuvid --enable-dxva2 --enable-d3d11va --enable-d3d12va --enable-ffnvcodec --enable-libvpl --enable-nvdec --enable-nvenc --enable-vaapi --enable-libshaderc --enable-vulkan --enable-libplacebo --enable-opencl --enable-libcdio --enable-libgme --enable-libmodplug --enable-libopenmpt --enable-libopencore-amrwb --enable-libmp3lame --enable-libshine --enable-libtheora --enable-libtwolame --enable-libvo-amrwbenc --enable-libcodec2 --enable-libilbc --enable-libgsm --enable-liblc3 --enable-libopencore-amrnb --enable-libopus --enable-libspeex --enable-libvorbis --enable-ladspa --enable-libbs2b --enable-libflite --enable-libmysofa --enable-librubberband --enable-libsoxr --enable-chromaprint
      libavutil      59. 39.100 / 59. 39.100
      libavcodec     61. 19.101 / 61. 19.101
      libavformat    61.  7.100 / 61.  7.100
      libavdevice    61.  3.100 / 61.  3.100
      libavfilter    10.  4.100 / 10.  4.100
      libswscale      8.  3.100 /  8.  3.100
      libswresample   5.  3.100 /  5.  3.100
      libpostproc    58.  3.100 / 58.  3.100
    [wav @ 00000283b12c4f00] Ignoring maximum wav data size, file may be invalid
    [wav @ 00000283b12c4f00] Packet corrupt (stream = 0, dts = NOPTS).
    Input #0, wav, from 'pipe:0':
      Duration: N/A, bitrate: 384 kb/s
      Stream #0:0: Audio: pcm_s16le ([1][0][0][0] / 0x0001), 24000 Hz, 1 channels, s16, 384 kb/s
      1.32 M-A:  0.000 fd=   0 aq=    0KB vq=    0KB sq=    0B

3. $ref = [uri]::EscapeDataString("https://samplelib.com/lib/preview/wav/sample-3s.wav")
   curl.exe -Ns "http://127.0.0.1:8000/synthesize/stream_get?engine=cosyvoice2&cosy_mode=cross&cosy_ref_url=$ref&max_chars=60&speed=1.1&text=Remote%20reference%20test" | ffplay -autoexit -nodisp -i pipe:0 
   - took 13 seconds and the audio was 

4. curl.exe -Ns "http://127.0.0.1:8000/synthesize/stream_get?engine=kokoro&voice=af_heart&max_chars=100&text=Hello%20from%20the%20GET%20stream" | ffplay -autoexit -nodisp -i pipe:0 
   - took 12 seconds and audio was very low
   - ffplay version 7.1.1-full_build-www.gyan.dev Copyright (c) 2003-2025 the FFmpeg developers
      built with gcc 14.2.0 (Rev1, Built by MSYS2 project)
      configuration: --enable-gpl --enable-version3 --enable-static --disable-w32threads --disable-autodetect --enable-fontconfig --enable-iconv --enable-gnutls --enable-lcms2 --enable-libxml2 --enable-gmp --enable-bzlib --enable-lzma --enable-libsnappy --enable-zlib --enable-librist --enable-libsrt --enable-libssh --enable-libzmq --enable-avisynth --enable-libbluray --enable-libcaca --enable-libdvdnav --enable-libdvdread --enable-sdl2 --enable-libaribb24 --enable-libaribcaption --enable-libdav1d --enable-libdavs2 --enable-libopenjpeg --enable-libquirc --enable-libuavs3d --enable-libxevd --enable-libzvbi --enable-libqrencode --enable-librav1e --enable-libsvtav1 --enable-libvvenc --enable-libwebp --enable-libx264 --enable-libx265 --enable-libxavs2 --enable-libxeve --enable-libxvid --enable-libaom --enable-libjxl --enable-libvpx --enable-mediafoundation --enable-libass --enable-frei0r --enable-libfreetype --enable-libfribidi --enable-libharfbuzz --enable-liblensfun --enable-libvidstab --enable-libvmaf --enable-libzimg --enable-amf --enable-cuda-llvm --enable-cuvid --enable-dxva2 --enable-d3d11va --enable-d3d12va --enable-ffnvcodec --enable-libvpl --enable-nvdec --enable-nvenc --enable-vaapi --enable-libshaderc --enable-vulkan --enable-libplacebo --enable-opencl --enable-libcdio --enable-libgme --enable-libmodplug --enable-libopenmpt --enable-libopencore-amrwb --enable-libmp3lame --enable-libshine --enable-libtheora --enable-libtwolame --enable-libvo-amrwbenc --enable-libcodec2 --enable-libilbc --enable-libgsm --enable-liblc3 --enable-libopencore-amrnb --enable-libopus --enable-libspeex --enable-libvorbis --enable-ladspa --enable-libbs2b --enable-libflite --enable-libmysofa --enable-librubberband --enable-libsoxr --enable-chromaprint
      libavutil      59. 39.100 / 59. 39.100
      libavcodec     61. 19.101 / 61. 19.101
      libavformat    61.  7.100 / 61.  7.100
      libavdevice    61.  3.100 / 61.  3.100
      libavfilter    10.  4.100 / 10.  4.100
      libswscale      8.  3.100 /  8.  3.100
      libswresample   5.  3.100 /  5.  3.100
      libpostproc    58.  3.100 / 58.  3.100
    [wav @ 0000026ad2294f00] Ignoring maximum wav data size, file may be invalid
    [wav @ 0000026ad2294f00] Packet corrupt (stream = 0, dts = NOPTS).
    Input #0, wav, from 'pipe:0':
      Duration: N/A, bitrate: 384 kb/s
      Stream #0:0: Audio: pcm_s16le ([1][0][0][0] / 0x0001), 24000 Hz, 1 channels, s16, 384 kb/s
      1.42 M-A:  0.000 fd=   0 aq=    0KB vq=    0KB sq=    0B

5. curl.exe -s -X POST "http://127.0.0.1:8000/synthesize/stream" -F "text=This is a streaming test." -F "engine=kokoro" -F "voice=af_heart" | ffplay -autoexit -nodisp -i pipe:0 
   - took less than a seconds and the audio was perfect. do not optimize changes for this test anymore and make sure any changes to other code don't break this test.
   - ffplay version 7.1.1-full_build-www.gyan.dev Copyright (c) 2003-2025 the FFmpeg developers
      built with gcc 14.2.0 (Rev1, Built by MSYS2 project)
      configuration: --enable-gpl --enable-version3 --enable-static --disable-w32threads --disable-autodetect --enable-fontconfig --enable-iconv --enable-gnutls --enable-lcms2 --enable-libxml2 --enable-gmp --enable-bzlib --enable-lzma --enable-libsnappy --enable-zlib --enable-librist --enable-libsrt --enable-libssh --enable-libzmq --enable-avisynth --enable-libbluray --enable-libcaca --enable-libdvdnav --enable-libdvdread --enable-sdl2 --enable-libaribb24 --enable-libaribcaption --enable-libdav1d --enable-libdavs2 --enable-libopenjpeg --enable-libquirc --enable-libuavs3d --enable-libxevd --enable-libzvbi --enable-libqrencode --enable-librav1e --enable-libsvtav1 --enable-libvvenc --enable-libwebp --enable-libx264 --enable-libx265 --enable-libxavs2 --enable-libxeve --enable-libxvid --enable-libaom --enable-libjxl --enable-libvpx --enable-mediafoundation --enable-libass --enable-frei0r --enable-libfreetype --enable-libfribidi --enable-libharfbuzz --enable-liblensfun --enable-libvidstab --enable-libvmaf --enable-libzimg --enable-amf --enable-cuda-llvm --enable-cuvid --enable-dxva2 --enable-d3d11va --enable-d3d12va --enable-ffnvcodec --enable-libvpl --enable-nvdec --enable-nvenc --enable-vaapi --enable-libshaderc --enable-vulkan --enable-libplacebo --enable-opencl --enable-libcdio --enable-libgme --enable-libmodplug --enable-libopenmpt --enable-libopencore-amrwb --enable-libmp3lame --enable-libshine --enable-libtheora --enable-libtwolame --enable-libvo-amrwbenc --enable-libcodec2 --enable-libilbc --enable-libgsm --enable-liblc3 --enable-libopencore-amrnb --enable-libopus --enable-libspeex --enable-libvorbis --enable-ladspa --enable-libbs2b --enable-libflite --enable-libmysofa --enable-librubberband --enable-libsoxr --enable-chromaprint
      libavutil      59. 39.100 / 59. 39.100
      libavcodec     61. 19.101 / 61. 19.101
      libavformat    61.  7.100 / 61.  7.100
      libavdevice    61.  3.100 / 61.  3.100
      libavfilter    10.  4.100 / 10.  4.100
      libswscale      8.  3.100 /  8.  3.100
      libswresample   5.  3.100 /  5.  3.100
      libpostproc    58.  3.100 / 58.  3.100
    [wav @ 000001bf11d13400] Ignoring maximum wav data size, file may be invalid
    [wav @ 000001bf11d13400] Packet corrupt (stream = 0, dts = NOPTS).
    Input #0, wav, from 'pipe:0':
      Duration: N/A, bitrate: 384 kb/s
      Stream #0:0: Audio: pcm_s16le ([1][0][0][0] / 0x0001), 24000 Hz, 1 channels, s16, 384 kb/s
      2.03 M-A:  0.000 fd=   0 aq=    0KB vq=    0KB sq=    0B

# TESTING RESULTS #3

### 1. CosyVoice2 (preset ref id)
   - curl.exe -Ns "http://127.0.0.1:8000/synthesize/stream_get?engine=cosyvoice2&cosy_mode=cross&cosy_ref_id=ref&max_chars=60&speed=1.1&text=Remote%20reference%20test" | ffplay -autoexit -nodisp -i pipe:0 
   - Response Time: no audio played
   - Audo Quality: na
   - Output:
     - ffplay version 7.1.1-full_build-www.gyan.dev Copyright (c) 2003-2025 the FFmpeg developers
        built with gcc 14.2.0 (Rev1, Built by MSYS2 project)
        configuration: --enable-gpl --enable-version3 --enable-static --disable-w32threads --disable-autodetect --enable-fontconfig --enable-iconv --enable-gnutls --enable-lcms2 --enable-libxml2 --enable-gmp --enable-bzlib --enable-lzma --enable-libsnappy --enable-zlib --enable-librist --enable-libsrt --enable-libssh --enable-libzmq --enable-avisynth --enable-libbluray --enable-libcaca --enable-libdvdnav --enable-libdvdread --enable-sdl2 --enable-libaribb24 --enable-libaribcaption --enable-libdav1d --enable-libdavs2 --enable-libopenjpeg --enable-libquirc --enable-libuavs3d --enable-libxevd --enable-libzvbi --enable-libqrencode --enable-librav1e --enable-libsvtav1 --enable-libvvenc --enable-libwebp --enable-libx264 --enable-libx265 --enable-libxavs2 --enable-libxeve --enable-libxvid --enable-libaom --enable-libjxl --enable-libvpx --enable-mediafoundation --enable-libass --enable-frei0r --enable-libfreetype --enable-libfribidi --enable-libharfbuzz --enable-liblensfun --enable-libvidstab --enable-libvmaf --enable-libzimg --enable-amf --enable-cuda-llvm --enable-cuvid --enable-dxva2 --enable-d3d11va --enable-d3d12va --enable-ffnvcodec --enable-libvpl --enable-nvdec --enable-nvenc --enable-vaapi --enable-libshaderc --enable-vulkan --enable-libplacebo --enable-opencl --enable-libcdio --enable-libgme --enable-libmodplug --enable-libopenmpt --enable-libopencore-amrwb --enable-libmp3lame --enable-libshine --enable-libtheora --enable-libtwolame --enable-libvo-amrwbenc --enable-libcodec2 --enable-libilbc --enable-libgsm --enable-liblc3 --enable-libopencore-amrnb --enable-libopus --enable-libspeex --enable-libvorbis --enable-ladspa --enable-libbs2b --enable-libflite --enable-libmysofa --enable-librubberband --enable-libsoxr --enable-chromaprint
        libavutil      59. 39.100 / 59. 39.100
        libavcodec     61. 19.101 / 61. 19.101
        libavformat    61.  7.100 / 61.  7.100
        libavdevice    61.  3.100 / 61.  3.100
        libavfilter    10.  4.100 / 10.  4.100
        libswscale      8.  3.100 /  8.  3.100
        libswresample   5.  3.100 /  5.  3.100
        libpostproc    58.  3.100 / 58.  3.100
      pipe:0: Invalid data found when processing inputB sq=    0B
   - Error Details:
     - INFO:     127.0.0.1:61810 - "POST /synthesize/stream HTTP/1.1" 200 OK
        INFO:     127.0.0.1:61822 - "GET /synthesize/stream_get?engine=cosyvoice2&cosy_mode=cross&cosy_ref_id=ref&max_chars=60&speed=1.1&text=Remote%20reference%20test HTTP/1.1" 500 Internal Server Error
        ERROR:    Exception in ASGI application
        Traceback (most recent call last):
          File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\uvicorn\protocols\http\httptools_impl.py", line 399, in run_asgi
            result = await app(  # type: ignore[func-returns-value]
          File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\uvicorn\middleware\proxy_headers.py", line 70, in __call__
            return await self.app(scope, receive, send)
          File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\fastapi\applications.py", line 1054, in __call__
            await super().__call__(scope, receive, send)
          File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\starlette\applications.py", line 113, in __call__
            await self.middleware_stack(scope, receive, send)
          File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\starlette\middleware\errors.py", line 187, in __call__
            raise exc
          File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\starlette\middleware\errors.py", line 165, in __call__
            await self.app(scope, receive, _send)
          File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\starlette\middleware\cors.py", line 85, in __call__
            await self.app(scope, receive, send)
          File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\starlette\middleware\exceptions.py", line 62, in __call__
            await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
          File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\starlette\_exception_handler.py", line 53, in wrapped_app
            raise exc
          File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\starlette\_exception_handler.py", line 42, in wrapped_app
            await app(scope, receive, sender)
          File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\starlette\routing.py", line 715, in __call__
            await self.middleware_stack(scope, receive, send)
          File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\starlette\routing.py", line 735, in app
            await route.handle(scope, receive, send)
          File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\starlette\routing.py", line 288, in handle
            await self.app(scope, receive, send)
          File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\starlette\routing.py", line 76, in app
            await wrap_app_handling_exceptions(app, request)(scope, receive, send)
          File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\starlette\_exception_handler.py", line 53, in wrapped_app
            raise exc
          File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\starlette\_exception_handler.py", line 42, in wrapped_app
            await app(scope, receive, sender)
          File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\starlette\routing.py", line 73, in app
            response = await f(request)
          File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\fastapi\routing.py", line 301, in app
            raw_response = await run_endpoint_function(
          File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\fastapi\routing.py", line 214, in run_endpoint_function
            return await run_in_threadpool(dependant.call, **values)
          File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\starlette\concurrency.py", line 39, in run_in_threadpool
            return await anyio.to_thread.run_sync(func, *args)
          File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\anyio\to_thread.py", line 56, in run_sync
            return await get_async_backend().run_sync_in_worker_thread(
          File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\anyio\_backends\_asyncio.py", line 2476, in run_sync_in_worker_thread
            return await future
          File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\anyio\_backends\_asyncio.py", line 967, in run
            result = context.run(func, *args)
          File "D:\01_Projects\Personal\tts-starter\app\api.py", line 241, in synthesize_stream_get
            sr, cosy_bytes = stream_cosyvoice2_cross(
          File "D:\01_Projects\Personal\tts-starter\app\utils\synthesize.py", line 294, in stream_cosyvoice2_cross
            cv = get_cosyvoice2()  # let the new policy pick CPU/GPU and FP16
          File "D:\01_Projects\Personal\tts-starter\app\services\models.py", line 131, in get_cosyvoice2
            root = _find_cosy_root()
        NameError: name '_find_cosy_root' is not defined 

### 2. CosyVoice2 (remote ref URL)
   - $ref = [uri]::EscapeDataString("https://samplelib.com/lib/preview/wav/sample-3s.wav")
   - curl.exe -Ns "http://127.0.0.1:8000/synthesize/stream_get?engine=cosyvoice2&cosy_mode=cross&cosy_ref_url=$ref&max_chars=60&speed=1.1&text=Remote%20reference%20test" | ffplay -autoexit -nodisp -i pipe:0 
   - Response Time: no audio played
   - Audo Quality: na
   - Output:
     - ffplay version 7.1.1-full_build-www.gyan.dev Copyright (c) 2003-2025 the FFmpeg developers
        built with gcc 14.2.0 (Rev1, Built by MSYS2 project)
        configuration: --enable-gpl --enable-version3 --enable-static --disable-w32threads --disable-autodetect --enable-fontconfig --enable-iconv --enable-gnutls --enable-lcms2 --enable-libxml2 --enable-gmp --enable-bzlib --enable-lzma --enable-libsnappy --enable-zlib --enable-librist --enable-libsrt --enable-libssh --enable-libzmq --enable-avisynth --enable-libbluray --enable-libcaca --enable-libdvdnav --enable-libdvdread --enable-sdl2 --enable-libaribb24 --enable-libaribcaption --enable-libdav1d --enable-libdavs2 --enable-libopenjpeg --enable-libquirc --enable-libuavs3d --enable-libxevd --enable-libzvbi --enable-libqrencode --enable-librav1e --enable-libsvtav1 --enable-libvvenc --enable-libwebp --enable-libx264 --enable-libx265 --enable-libxavs2 --enable-libxeve --enable-libxvid --enable-libaom --enable-libjxl --enable-libvpx --enable-mediafoundation --enable-libass --enable-frei0r --enable-libfreetype --enable-libfribidi --enable-libharfbuzz --enable-liblensfun --enable-libvidstab --enable-libvmaf --enable-libzimg --enable-amf --enable-cuda-llvm --enable-cuvid --enable-dxva2 --enable-d3d11va --enable-d3d12va --enable-ffnvcodec --enable-libvpl --enable-nvdec --enable-nvenc --enable-vaapi --enable-libshaderc --enable-vulkan --enable-libplacebo --enable-opencl --enable-libcdio --enable-libgme --enable-libmodplug --enable-libopenmpt --enable-libopencore-amrwb --enable-libmp3lame --enable-libshine --enable-libtheora --enable-libtwolame --enable-libvo-amrwbenc --enable-libcodec2 --enable-libilbc --enable-libgsm --enable-liblc3 --enable-libopencore-amrnb --enable-libopus --enable-libspeex --enable-libvorbis --enable-ladspa --enable-libbs2b --enable-libflite --enable-libmysofa --enable-librubberband --enable-libsoxr --enable-chromaprint
        libavutil      59. 39.100 / 59. 39.100
        libavcodec     61. 19.101 / 61. 19.101
        libavformat    61.  7.100 / 61.  7.100
        libavdevice    61.  3.100 / 61.  3.100
        libavfilter    10.  4.100 / 10.  4.100
        libswscale      8.  3.100 /  8.  3.100
        libswresample   5.  3.100 /  5.  3.100
        libpostproc    58.  3.100 / 58.  3.100
      pipe:0: Invalid data found when processing inputB sq=    0B
          nan    :  0.000 fd=   0 aq=    0KB vq=    0KB sq=    0B
   - Error Details:
     - INFO:     127.0.0.1:54233 - "GET /synthesize/stream_get?engine=cosyvoice2&cosy_mode=cross&cosy_ref_id=ref&max_chars=60&speed=1.1&text=Remote%20reference%20test HTTP/1.1" 500 Internal Server Error
        ERROR:    Exception in ASGI application
        Traceback (most recent call last):
          File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\uvicorn\protocols\http\httptools_impl.py", line 399, in run_asgi
            result = await app(  # type: ignore[func-returns-value]
          File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\uvicorn\middleware\proxy_headers.py", line 70, in __call__
            return await self.app(scope, receive, send)
          File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\fastapi\applications.py", line 1054, in __call__
            await super().__call__(scope, receive, send)
          File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\starlette\applications.py", line 113, in __call__
            await self.middleware_stack(scope, receive, send)
          File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\starlette\middleware\errors.py", line 187, in __call__
            raise exc
          File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\starlette\middleware\errors.py", line 165, in __call__
            await self.app(scope, receive, _send)
          File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\starlette\middleware\cors.py", line 85, in __call__
            await self.app(scope, receive, send)
          File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\starlette\middleware\exceptions.py", line 62, in __call__
            await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
          File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\starlette\_exception_handler.py", line 53, in wrapped_app
            raise exc
          File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\starlette\_exception_handler.py", line 42, in wrapped_app
            await app(scope, receive, sender)
          File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\starlette\routing.py", line 715, in __call__
            await self.middleware_stack(scope, receive, send)
          File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\starlette\routing.py", line 735, in app
            await route.handle(scope, receive, send)
          File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\starlette\routing.py", line 288, in handle
            await self.app(scope, receive, send)
          File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\starlette\routing.py", line 76, in app
            await wrap_app_handling_exceptions(app, request)(scope, receive, send)
          File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\starlette\_exception_handler.py", line 53, in wrapped_app
            raise exc
          File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\starlette\_exception_handler.py", line 42, in wrapped_app
            await app(scope, receive, sender)
          File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\starlette\routing.py", line 73, in app
            response = await f(request)
          File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\fastapi\routing.py", line 301, in app
            raw_response = await run_endpoint_function(
          File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\fastapi\routing.py", line 214, in run_endpoint_function
            return await run_in_threadpool(dependant.call, **values)
          File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\starlette\concurrency.py", line 39, in run_in_threadpool
            return await anyio.to_thread.run_sync(func, *args)
          File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\anyio\to_thread.py", line 56, in run_sync
            return await get_async_backend().run_sync_in_worker_thread(
          File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\anyio\_backends\_asyncio.py", line 2476, in run_sync_in_worker_thread
            return await future
          File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\anyio\_backends\_asyncio.py", line 967, in run
            result = context.run(func, *args)
          File "D:\01_Projects\Personal\tts-starter\app\api.py", line 241, in synthesize_stream_get
            sr, cosy_bytes = stream_cosyvoice2_cross(
          File "D:\01_Projects\Personal\tts-starter\app\utils\synthesize.py", line 294, in stream_cosyvoice2_cross
            cv = get_cosyvoice2()  # let the new policy pick CPU/GPU and FP16
          File "D:\01_Projects\Personal\tts-starter\app\services\models.py", line 131, in get_cosyvoice2
            root = _find_cosy_root()
        NameError: name '_find_cosy_root' is not defined 

### 3. Kokoro — GET *Happy with results, no changes needed*
   - curl.exe -Ns "http://127.0.0.1:8000/synthesize/stream_get?engine=kokoro&voice=af_heart&max_chars=100&text=Hello%20from%20the%20GET%20stream" | ffplay -autoexit -nodisp -i pipe:0 
   - Response Time: 1.5 seconds
   - Audo Quality: Perfect
   - Output:
     - ffplay version 7.1.1-full_build-www.gyan.dev Copyright (c) 2003-2025 the FFmpeg developers
        built with gcc 14.2.0 (Rev1, Built by MSYS2 project)
        configuration: --enable-gpl --enable-version3 --enable-static --disable-w32threads --disable-autodetect --enable-fontconfig --enable-iconv --enable-gnutls --enable-lcms2 --enable-libxml2 --enable-gmp --enable-bzlib --enable-lzma --enable-libsnappy --enable-zlib --enable-librist --enable-libsrt --enable-libssh --enable-libzmq --enable-avisynth --enable-libbluray --enable-libcaca --enable-libdvdnav --enable-libdvdread --enable-sdl2 --enable-libaribb24 --enable-libaribcaption --enable-libdav1d --enable-libdavs2 --enable-libopenjpeg --enable-libquirc --enable-libuavs3d --enable-libxevd --enable-libzvbi --enable-libqrencode --enable-librav1e --enable-libsvtav1 --enable-libvvenc --enable-libwebp --enable-libx264 --enable-libx265 --enable-libxavs2 --enable-libxeve --enable-libxvid --enable-libaom --enable-libjxl --enable-libvpx --enable-mediafoundation --enable-libass --enable-frei0r --enable-libfreetype --enable-libfribidi --enable-libharfbuzz --enable-liblensfun --enable-libvidstab --enable-libvmaf --enable-libzimg --enable-amf --enable-cuda-llvm --enable-cuvid --enable-dxva2 --enable-d3d11va --enable-d3d12va --enable-ffnvcodec --enable-libvpl --enable-nvdec --enable-nvenc --enable-vaapi --enable-libshaderc --enable-vulkan --enable-libplacebo --enable-opencl --enable-libcdio --enable-libgme --enable-libmodplug --enable-libopenmpt --enable-libopencore-amrwb --enable-libmp3lame --enable-libshine --enable-libtheora --enable-libtwolame --enable-libvo-amrwbenc --enable-libcodec2 --enable-libilbc --enable-libgsm --enable-liblc3 --enable-libopencore-amrnb --enable-libopus --enable-libspeex --enable-libvorbis --enable-ladspa --enable-libbs2b --enable-libflite --enable-libmysofa --enable-librubberband --enable-libsoxr --enable-chromaprint
        libavutil      59. 39.100 / 59. 39.100
        libavcodec     61. 19.101 / 61. 19.101
        libavformat    61.  7.100 / 61.  7.100
        libavdevice    61.  3.100 / 61.  3.100
        libavfilter    10.  4.100 / 10.  4.100
        libswscale      8.  3.100 /  8.  3.100
        libswresample   5.  3.100 /  5.  3.100
        libpostproc    58.  3.100 / 58.  3.100
      [wav @ 000001abcad44f00] Ignoring maximum wav data size, file may be invalid
      [wav @ 000001abcad44f00] Packet corrupt (stream = 0, dts = NOPTS).
      Input #0, wav, from 'pipe:0':
        Duration: N/A, bitrate: 384 kb/s
        Stream #0:0: Audio: pcm_s16le ([1][0][0][0] / 0x0001), 24000 Hz, 

### 4. Kokoro — POST *Happy with results, no changes needed*
   - curl.exe -s -X POST "http://127.0.0.1:8000/synthesize/stream" -F "text=This is a streaming test." -F "engine=kokoro" -F "voice=af_heart" | ffplay -autoexit -nodisp -i pipe:0 
   - Response Time: less than a second
   - Audo Quality: Perfect
   - Output:
     - ffplay version 7.1.1-full_build-www.gyan.dev Copyright (c) 2003-2025 the FFmpeg developers
        built with gcc 14.2.0 (Rev1, Built by MSYS2 project)
        configuration: --enable-gpl --enable-version3 --enable-static --disable-w32threads --disable-autodetect --enable-fontconfig --enable-iconv --enable-gnutls --enable-lcms2 --enable-libxml2 --enable-gmp --enable-bzlib --enable-lzma --enable-libsnappy --enable-zlib --enable-librist --enable-libsrt --enable-libssh --enable-libzmq --enable-avisynth --enable-libbluray --enable-libcaca --enable-libdvdnav --enable-libdvdread --enable-sdl2 --enable-libaribb24 --enable-libaribcaption --enable-libdav1d --enable-libdavs2 --enable-libopenjpeg --enable-libquirc --enable-libuavs3d --enable-libxevd --enable-libzvbi --enable-libqrencode --enable-librav1e --enable-libsvtav1 --enable-libvvenc --enable-libwebp --enable-libx264 --enable-libx265 --enable-libxavs2 --enable-libxeve --enable-libxvid --enable-libaom --enable-libjxl --enable-libvpx --enable-mediafoundation --enable-libass --enable-frei0r --enable-libfreetype --enable-libfribidi --enable-libharfbuzz --enable-liblensfun --enable-libvidstab --enable-libvmaf --enable-libzimg --enable-amf --enable-cuda-llvm --enable-cuvid --enable-dxva2 --enable-d3d11va --enable-d3d12va --enable-ffnvcodec --enable-libvpl --enable-nvdec --enable-nvenc --enable-vaapi --enable-libshaderc --enable-vulkan --enable-libplacebo --enable-opencl --enable-libcdio --enable-libgme --enable-libmodplug --enable-libopenmpt --enable-libopencore-amrwb --enable-libmp3lame --enable-libshine --enable-libtheora --enable-libtwolame --enable-libvo-amrwbenc --enable-libcodec2 --enable-libilbc --enable-libgsm --enable-liblc3 --enable-libopencore-amrnb --enable-libopus --enable-libspeex --enable-libvorbis --enable-ladspa --enable-libbs2b --enable-libflite --enable-libmysofa --enable-librubberband --enable-libsoxr --enable-chromaprint
        libavutil      59. 39.100 / 59. 39.100
        libavcodec     61. 19.101 / 61. 19.101
        libavformat    61.  7.100 / 61.  7.100
        libavdevice    61.  3.100 / 61.  3.100
        libavfilter    10.  4.100 / 10.  4.100
        libswscale      8.  3.100 /  8.  3.100
        libswresample   5.  3.100 /  5.  3.100
        libpostproc    58.  3.100 / 58.  3.100
      [wav @ 0000020049784f00] Ignoring maximum wav data size, file may be invalid
      [wav @ 0000020049784f00] Packet corrupt (stream = 0, dts = NOPTS).
      Input #0, wav, from 'pipe:0':
        Duration: N/A, bitrate: 384 kb/s
        Stream #0:0: Audio: pcm_s16le ([1][0][0][0] / 0x0001), 24000 Hz, 1 channels, s16, 384 kb/s
        2.01 M-A:  0.000 fd=   0 aq=    0KB vq=    0KB sq=    0B

### 5. PCM — lower latency, no warnings
   - curl.exe -Ns "http://127.0.0.1:8000/synthesize/stream_get?engine=cosyvoice2&cosy_mode=cross&cosy_ref_id=ref&max_chars=60&speed=1.1&fmt=pcm&text=Remote%20reference%20test" | ffplay -autoexit -nodisp -f s16le -ar 24000 -ac 1 -i pipe:0
   - Response Time: no audio played
   - Audo Quality: na
   - Output:
     - ffplay version 7.1.1-full_build-www.gyan.dev Copyright (c) 2003-2025 the FFmpeg developers
        built with gcc 14.2.0 (Rev1, Built by MSYS2 project)
        configuration: --enable-gpl --enable-version3 --enable-static --disable-w32threads --disable-autodetect --enable-fontconfig --enable-iconv --enable-gnutls --enable-lcms2 --enable-libxml2 --enable-gmp --enable-bzlib --enable-lzma --enable-libsnappy --enable-zlib --enable-librist --enable-libsrt --enable-libssh --enable-libzmq --enable-avisynth --enable-libbluray --enable-libcaca --enable-libdvdnav --enable-libdvdread --enable-sdl2 --enable-libaribb24 --enable-libaribcaption --enable-libdav1d --enable-libdavs2 --enable-libopenjpeg --enable-libquirc --enable-libuavs3d --enable-libxevd --enable-libzvbi --enable-libqrencode --enable-librav1e --enable-libsvtav1 --enable-libvvenc --enable-libwebp --enable-libx264 --enable-libx265 --enable-libxavs2 --enable-libxeve --enable-libxvid --enable-libaom --enable-libjxl --enable-libvpx --enable-mediafoundation --enable-libass --enable-frei0r --enable-libfreetype --enable-libfribidi --enable-libharfbuzz --enable-liblensfun --enable-libvidstab --enable-libvmaf --enable-libzimg --enable-amf --enable-cuda-llvm --enable-cuvid --enable-dxva2 --enable-d3d11va --enable-d3d12va --enable-ffnvcodec --enable-libvpl --enable-nvdec --enable-nvenc --enable-vaapi --enable-libshaderc --enable-vulkan --enable-libplacebo --enable-opencl --enable-libcdio --enable-libgme --enable-libmodplug --enable-libopenmpt --enable-libopencore-amrwb --enable-libmp3lame --enable-libshine --enable-libtheora --enable-libtwolame --enable-libvo-amrwbenc --enable-libcodec2 --enable-libilbc --enable-libgsm --enable-liblc3 --enable-libopencore-amrnb --enable-libopus --enable-libspeex --enable-libvorbis --enable-ladspa --enable-libbs2b --enable-libflite --enable-libmysofa --enable-librubberband --enable-libsoxr --enable-chromaprint
        libavutil      59. 39.100 / 59. 39.100
        libavcodec     61. 19.101 / 61. 19.101
        libavformat    61.  7.100 / 61.  7.100
        libavdevice    61.  3.100 / 61.  3.100
        libavfilter    10.  4.100 / 10.  4.100
        libswscale      8.  3.100 /  8.  3.100
        libswresample   5.  3.100 /  5.  3.100
        libpostproc    58.  3.100 / 58.  3.100
      Failed to set value '1' for option 'ac': Option not found
   - Error Details: 
     - INFO:     127.0.0.1:62076 - "GET /synthesize/stream_get?engine=cosyvoice2&cosy_mode=cross&cosy_ref_id=ref&max_chars=60&speed=1.1&fmt=pcm&text=Remote%20reference%20test HTTP/1.1" 500 Internal Server Error
        ERROR:    Exception in ASGI application
        Traceback (most recent call last):
          File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\uvicorn\protocols\http\httptools_impl.py", line 399, in run_asgi
            result = await app(  # type: ignore[func-returns-value]
          File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\uvicorn\middleware\proxy_headers.py", line 70, in __call__
            return await self.app(scope, receive, send)
          File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\fastapi\applications.py", line 1054, in __call__
            await super().__call__(scope, receive, send)
          File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\starlette\applications.py", line 113, in __call__
            await self.middleware_stack(scope, receive, send)
          File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\starlette\middleware\errors.py", line 187, in __call__
            raise exc
          File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\starlette\middleware\errors.py", line 165, in __call__
            await self.app(scope, receive, _send)
          File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\starlette\middleware\cors.py", line 85, in __call__
            await self.app(scope, receive, send)
          File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\starlette\middleware\exceptions.py", line 62, in __call__
            await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
          File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\starlette\_exception_handler.py", line 53, in wrapped_app
            raise exc
          File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\starlette\_exception_handler.py", line 42, in wrapped_app
            await app(scope, receive, sender)
          File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\starlette\routing.py", line 715, in __call__
            await self.middleware_stack(scope, receive, send)
          File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\starlette\routing.py", line 735, in app
            await route.handle(scope, receive, send)
          File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\starlette\routing.py", line 288, in handle
            await self.app(scope, receive, send)
          File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\starlette\routing.py", line 76, in app
            await wrap_app_handling_exceptions(app, request)(scope, receive, send)
          File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\starlette\_exception_handler.py", line 53, in wrapped_app
            raise exc
          File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\starlette\_exception_handler.py", line 42, in wrapped_app
            await app(scope, receive, sender)
          File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\starlette\routing.py", line 73, in app
            response = await f(request)
          File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\fastapi\routing.py", line 301, in app
            raw_response = await run_endpoint_function(
          File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\fastapi\routing.py", line 214, in run_endpoint_function
            return await run_in_threadpool(dependant.call, **values)
          File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\starlette\concurrency.py", line 39, in run_in_threadpool
            return await anyio.to_thread.run_sync(func, *args)
          File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\anyio\to_thread.py", line 56, in run_sync
            return await get_async_backend().run_sync_in_worker_thread(
          File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\anyio\_backends\_asyncio.py", line 2476, in run_sync_in_worker_thread
            return await future
          File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\anyio\_backends\_asyncio.py", line 967, in run
            result = context.run(func, *args)
          File "D:\01_Projects\Personal\tts-starter\app\api.py", line 241, in synthesize_stream_get
            sr, cosy_bytes = stream_cosyvoice2_cross(
          File "D:\01_Projects\Personal\tts-starter\app\utils\synthesize.py", line 294, in stream_cosyvoice2_cross
            cv = get_cosyvoice2()  # let the new policy pick CPU/GPU and FP16
          File "D:\01_Projects\Personal\tts-starter\app\services\models.py", line 131, in get_cosyvoice2
            root = _find_cosy_root()
        NameError: name '_find_cosy_root' is not defined  

### 6. WAV - current default
   - curl.exe -Ns "http://127.0.0.1:8000/synthesize/stream_get?engine=cosyvoice2&cosy_mode=cross&cosy_ref_id=ref&max_chars=60&speed=1.1&text=Remote%20reference%20test" | ffplay -autoexit -nodisp -i pipe:0
   - Response Time: no audio played
   - Audo Quality: na
   - Output:
     - ffplay version 7.1.1-full_build-www.gyan.dev Copyright (c) 2003-2025 the FFmpeg developers
      built with gcc 14.2.0 (Rev1, Built by MSYS2 project)
      configuration: --enable-gpl --enable-version3 --enable-static --disable-w32threads --disable-autodetect --enable-fontconfig --enable-iconv --enable-gnutls --enable-lcms2 --enable-libxml2 --enable-gmp --enable-bzlib --enable-lzma --enable-libsnappy --enable-zlib --enable-librist --enable-libsrt --enable-libssh --enable-libzmq --enable-avisynth --enable-libbluray --enable-libcaca --enable-libdvdnav --enable-libdvdread --enable-sdl2 --enable-libaribb24 --enable-libaribcaption --enable-libdav1d --enable-libdavs2 --enable-libopenjpeg --enable-libquirc --enable-libuavs3d --enable-libxevd --enable-libzvbi --enable-libqrencode --enable-librav1e --enable-libsvtav1 --enable-libvvenc --enable-libwebp --enable-libx264 --enable-libx265 --enable-libxavs2 --enable-libxeve --enable-libxvid --enable-libaom --enable-libjxl --enable-libvpx --enable-mediafoundation --enable-libass --enable-frei0r --enable-libfreetype --enable-libfribidi --enable-libharfbuzz --enable-liblensfun --enable-libvidstab --enable-libvmaf --enable-libzimg --enable-amf --enable-cuda-llvm --enable-cuvid --enable-dxva2 --enable-d3d11va --enable-d3d12va --enable-ffnvcodec --enable-libvpl --enable-nvdec --enable-nvenc --enable-vaapi --enable-libshaderc --enable-vulkan --enable-libplacebo --enable-opencl --enable-libcdio --enable-libgme --enable-libmodplug --enable-libopenmpt --enable-libopencore-amrwb --enable-libmp3lame --enable-libshine --enable-libtheora --enable-libtwolame --enable-libvo-amrwbenc --enable-libcodec2 --enable-libilbc --enable-libgsm --enable-liblc3 --enable-libopencore-amrnb --enable-libopus --enable-libspeex --enable-libvorbis --enable-ladspa --enable-libbs2b --enable-libflite --enable-libmysofa --enable-librubberband --enable-libsoxr --enable-chromaprint
      libavutil      59. 39.100 / 59. 39.100
      libavcodec     61. 19.101 / 61. 19.101
      libavformat    61.  7.100 / 61.  7.100
      libavdevice    61.  3.100 / 61.  3.100
      libavfilter    10.  4.100 / 10.  4.100
      libswscale      8.  3.100 /  8.  3.100
      libswresample   5.  3.100 /  5.  3.100
      libpostproc    58.  3.100 / 58.  3.100
    pipe:0: Invalid data found when processing inputB sq=    0B
   - Error Details:
     - INFO:     127.0.0.1:65030 - "GET /synthesize/stream_get?engine=cosyvoice2&cosy_mode=cross&cosy_ref_id=ref&max_chars=60&speed=1.1&text=Remote%20reference%20test HTTP/1.1" 500 Internal Server Error
        ERROR:    Exception in ASGI application
        Traceback (most recent call last):
          File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\uvicorn\protocols\http\httptools_impl.py", line 399, in run_asgi
            result = await app(  # type: ignore[func-returns-value]
          File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\uvicorn\middleware\proxy_headers.py", line 70, in __call__
            return await self.app(scope, receive, send)
          File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\fastapi\applications.py", line 1054, in __call__
            await super().__call__(scope, receive, send)
          File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\starlette\applications.py", line 113, in __call__
            await self.middleware_stack(scope, receive, send)
          File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\starlette\middleware\errors.py", line 187, in __call__
            raise exc
          File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\starlette\middleware\errors.py", line 165, in __call__
            await self.app(scope, receive, _send)
          File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\starlette\middleware\cors.py", line 85, in __call__
            await self.app(scope, receive, send)
          File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\starlette\middleware\exceptions.py", line 62, in __call__
            await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
          File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\starlette\_exception_handler.py", line 53, in wrapped_app
            raise exc
          File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\starlette\_exception_handler.py", line 42, in wrapped_app
            await app(scope, receive, sender)
          File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\starlette\routing.py", line 715, in __call__
            await self.middleware_stack(scope, receive, send)
          File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\starlette\routing.py", line 735, in app
            await route.handle(scope, receive, send)
          File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\starlette\routing.py", line 288, in handle
            await self.app(scope, receive, send)
          File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\starlette\routing.py", line 76, in app
            await wrap_app_handling_exceptions(app, request)(scope, receive, send)
          File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\starlette\_exception_handler.py", line 53, in wrapped_app
            raise exc
          File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\starlette\_exception_handler.py", line 42, in wrapped_app
            await app(scope, receive, sender)
          File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\starlette\routing.py", line 73, in app
            response = await f(request)
          File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\fastapi\routing.py", line 301, in app
            raw_response = await run_endpoint_function(
          File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\fastapi\routing.py", line 214, in run_endpoint_function
            return await run_in_threadpool(dependant.call, **values)
          File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\starlette\concurrency.py", line 39, in run_in_threadpool
            return await anyio.to_thread.run_sync(func, *args)
          File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\anyio\to_thread.py", line 56, in run_sync
            return await get_async_backend().run_sync_in_worker_thread(
          File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\anyio\_backends\_asyncio.py", line 2476, in run_sync_in_worker_thread
            return await future
          File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\anyio\_backends\_asyncio.py", line 967, in run
            result = context.run(func, *args)
          File "D:\01_Projects\Personal\tts-starter\app\api.py", line 241, in synthesize_stream_get
            sr, cosy_bytes = stream_cosyvoice2_cross(
          File "D:\01_Projects\Personal\tts-starter\app\utils\synthesize.py", line 294, in stream_cosyvoice2_cross
            cv = get_cosyvoice2()  # let the new policy pick CPU/GPU and FP16
          File "D:\01_Projects\Personal\tts-starter\app\services\models.py", line 131, in get_cosyvoice2
            root = _find_cosy_root()
        NameError: name '_find_cosy_root' is not defined 

### 7. Kokoro - GET (PCM)
   - curl.exe -Ns "http://127.0.0.1:8000/synthesize/stream_get?engine=kokoro&voice=af_heart&max_chars=100&fmt=pcm&text=Hello%20from%20the%20GET%20stream" | ffplay -autoexit -nodisp -f s16le -ar 24000 -i pipe:0
   - Response Time: no audio played
   - Audo Quality: na
   - Output:
     - ffplay version 7.1.1-full_build-www.gyan.dev Copyright (c) 2003-2025 the FFmpeg developers
        built with gcc 14.2.0 (Rev1, Built by MSYS2 project)
        configuration: --enable-gpl --enable-version3 --enable-static --disable-w32threads --disable-autodetect --enable-fontconfig --enable-iconv --enable-gnutls --enable-lcms2 --enable-libxml2 --enable-gmp --enable-bzlib --enable-lzma --enable-libsnappy --enable-zlib --enable-librist --enable-libsrt --enable-libssh --enable-libzmq --enable-avisynth --enable-libbluray --enable-libcaca --enable-libdvdnav --enable-libdvdread --enable-sdl2 --enable-libaribb24 --enable-libaribcaption --enable-libdav1d --enable-libdavs2 --enable-libopenjpeg --enable-libquirc --enable-libuavs3d --enable-libxevd --enable-libzvbi --enable-libqrencode --enable-librav1e --enable-libsvtav1 --enable-libvvenc --enable-libwebp --enable-libx264 --enable-libx265 --enable-libxavs2 --enable-libxeve --enable-libxvid --enable-libaom --enable-libjxl --enable-libvpx --enable-mediafoundation --enable-libass --enable-frei0r --enable-libfreetype --enable-libfribidi --enable-libharfbuzz --enable-liblensfun --enable-libvidstab --enable-libvmaf --enable-libzimg --enable-amf --enable-cuda-llvm --enable-cuvid --enable-dxva2 --enable-d3d11va --enable-d3d12va --enable-ffnvcodec --enable-libvpl --enable-nvdec --enable-nvenc --enable-vaapi --enable-libshaderc --enable-vulkan --enable-libplacebo --enable-opencl --enable-libcdio --enable-libgme --enable-libmodplug --enable-libopenmpt --enable-libopencore-amrwb --enable-libmp3lame --enable-libshine --enable-libtheora --enable-libtwolame --enable-libvo-amrwbenc --enable-libcodec2 --enable-libilbc --enable-libgsm --enable-liblc3 --enable-libopencore-amrnb --enable-libopus --enable-libspeex --enable-libvorbis --enable-ladspa --enable-libbs2b --enable-libflite --enable-libmysofa --enable-librubberband --enable-libsoxr --enable-chromaprint
        libavutil      59. 39.100 / 59. 39.100
        libavcodec     61. 19.101 / 61. 19.101
        libavformat    61.  7.100 / 61.  7.100
        libavdevice    61.  3.100 / 61.  3.100
        libavfilter    10.  4.100 / 10.  4.100
        libswscale      8.  3.100 /  8.  3.100
        libswresample   5.  3.100 /  5.  3.100
        libpostproc    58.  3.100 / 58.  3.100
      Failed to set value '1' for option 'ac': Option not found
      ResourceUnavailable: Program 'curl.exe' failed to run: The pipe is being closed.At line:1 char:1
      + curl.exe -Ns "http://127.0.0.1:8000/synthesize/stream_get?engine=koko …
      + ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~.
   - Error Details:
    - INFO:     127.0.0.1:65106 - "GET /synthesize/stream_get?engine=kokoro&voice=af_heart&max_chars=100&fmt=pcm&text=Hello%20from%20the%20GET%20stream HTTP/1.1" 200 OK 

### 8. Kokoro - GET (WAV)  *Happy with results, no changes needed*
   - curl.exe -Ns "http://127.0.0.1:8000/synthesize/stream_get?engine=kokoro&voice=af_heart&max_chars=100&text=Hello%20from%20the%20GET%20stream" | ffplay -autoexit -nodisp -i pipe:0
   - Response Time: less than 1 second
   - Audo Quality: Perfect
   - Output:
     - ffplay version 7.1.1-full_build-www.gyan.dev Copyright (c) 2003-2025 the FFmpeg developers
        built with gcc 14.2.0 (Rev1, Built by MSYS2 project)
        configuration: --enable-gpl --enable-version3 --enable-static --disable-w32threads --disable-autodetect --enable-fontconfig --enable-iconv --enable-gnutls --enable-lcms2 --enable-libxml2 --enable-gmp --enable-bzlib --enable-lzma --enable-libsnappy --enable-zlib --enable-librist --enable-libsrt --enable-libssh --enable-libzmq --enable-avisynth --enable-libbluray --enable-libcaca --enable-libdvdnav --enable-libdvdread --enable-sdl2 --enable-libaribb24 --enable-libaribcaption --enable-libdav1d --enable-libdavs2 --enable-libopenjpeg --enable-libquirc --enable-libuavs3d --enable-libxevd --enable-libzvbi --enable-libqrencode --enable-librav1e --enable-libsvtav1 --enable-libvvenc --enable-libwebp --enable-libx264 --enable-libx265 --enable-libxavs2 --enable-libxeve --enable-libxvid --enable-libaom --enable-libjxl --enable-libvpx --enable-mediafoundation --enable-libass --enable-frei0r --enable-libfreetype --enable-libfribidi --enable-libharfbuzz --enable-liblensfun --enable-libvidstab --enable-libvmaf --enable-libzimg --enable-amf --enable-cuda-llvm --enable-cuvid --enable-dxva2 --enable-d3d11va --enable-d3d12va --enable-ffnvcodec --enable-libvpl --enable-nvdec --enable-nvenc --enable-vaapi --enable-libshaderc --enable-vulkan --enable-libplacebo --enable-opencl --enable-libcdio --enable-libgme --enable-libmodplug --enable-libopenmpt --enable-libopencore-amrwb --enable-libmp3lame --enable-libshine --enable-libtheora --enable-libtwolame --enable-libvo-amrwbenc --enable-libcodec2 --enable-libilbc --enable-libgsm --enable-liblc3 --enable-libopencore-amrnb --enable-libopus --enable-libspeex --enable-libvorbis --enable-ladspa --enable-libbs2b --enable-libflite --enable-libmysofa --enable-librubberband --enable-libsoxr --enable-chromaprint
        libavutil      59. 39.100 / 59. 39.100
        libavcodec     61. 19.101 / 61. 19.101
        libavformat    61.  7.100 / 61.  7.100
        libavdevice    61.  3.100 / 61.  3.100
        libavfilter    10.  4.100 / 10.  4.100
        libswscale      8.  3.100 /  8.  3.100
        libswresample   5.  3.100 /  5.  3.100
        libpostproc    58.  3.100 / 58.  3.100
      [wav @ 000001e965b53400] Ignoring maximum wav data size, file may be invalid
      [wav @ 000001e965b53400] Packet corrupt (stream = 0, dts = NOPTS).
      Input #0, wav, from 'pipe:0':
        Duration: N/A, bitrate: 384 kb/s
        Stream #0:0: Audio: pcm_s16le ([1][0][0][0] / 0x0001), 24000 Hz, 1 channels, s16, 384 kb/s
        2.10 M-A:  0.000 fd=   0 aq=    0KB vq=    0KB sq=    0B

### 9. Kokoro — POST (your fast path) [PCM]  *Happy with results, no changes needed*
   - curl.exe -s -X POST "http://127.0.0.1:8000/synthesize/stream" -F "text=This is a streaming test." -F "engine=kokoro" -F "voice=af_heart" -F "fmt=pcm" | ffplay -autoexit -nodisp -f s16le -ar 24000 -ac 1 -i pipe:0
   - Response Time: less than 1 second
   - Audo Quality: Perfect
   - Output:
     - ffplay version 7.1.1-full_build-www.gyan.dev Copyright (c) 2003-2025 the FFmpeg developers
        built with gcc 14.2.0 (Rev1, Built by MSYS2 project)
        configuration: --enable-gpl --enable-version3 --enable-static --disable-w32threads --disable-autodetect --enable-fontconfig --enable-iconv --enable-gnutls --enable-lcms2 --enable-libxml2 --enable-gmp --enable-bzlib --enable-lzma --enable-libsnappy --enable-zlib --enable-librist --enable-libsrt --enable-libssh --enable-libzmq --enable-avisynth --enable-libbluray --enable-libcaca --enable-libdvdnav --enable-libdvdread --enable-sdl2 --enable-libaribb24 --enable-libaribcaption --enable-libdav1d --enable-libdavs2 --enable-libopenjpeg --enable-libquirc --enable-libuavs3d --enable-libxevd --enable-libzvbi --enable-libqrencode --enable-librav1e --enable-libsvtav1 --enable-libvvenc --enable-libwebp --enable-libx264 --enable-libx265 --enable-libxavs2 --enable-libxeve --enable-libxvid --enable-libaom --enable-libjxl --enable-libvpx --enable-mediafoundation --enable-libass --enable-frei0r --enable-libfreetype --enable-libfribidi --enable-libharfbuzz --enable-liblensfun --enable-libvidstab --enable-libvmaf --enable-libzimg --enable-amf --enable-cuda-llvm --enable-cuvid --enable-dxva2 --enable-d3d11va --enable-d3d12va --enable-ffnvcodec --enable-libvpl --enable-nvdec --enable-nvenc --enable-vaapi --enable-libshaderc --enable-vulkan --enable-libplacebo --enable-opencl --enable-libcdio --enable-libgme --enable-libmodplug --enable-libopenmpt --enable-libopencore-amrwb --enable-libmp3lame --enable-libshine --enable-libtheora --enable-libtwolame --enable-libvo-amrwbenc --enable-libcodec2 --enable-libilbc --enable-libgsm --enable-liblc3 --enable-libopencore-amrnb --enable-libopus --enable-libspeex --enable-libvorbis --enable-ladspa --enable-libbs2b --enable-libflite --enable-libmysofa --enable-librubberband --enable-libsoxr --enable-chromaprint
        libavutil      59. 39.100 / 59. 39.100
        libavcodec     61. 19.101 / 61. 19.101
        libavformat    61.  7.100 / 61.  7.100
        libavdevice    61.  3.100 / 61.  3.100
        libavfilter    10.  4.100 / 10.  4.100
        libswscale      8.  3.100 /  8.  3.100
        libswresample   5.  3.100 /  5.  3.100
        libpostproc    58.  3.100 / 58.  3.100
      [wav @ 000001cd2dce3400] Ignoring maximum wav data size, file may be invalid
      [wav @ 000001cd2dce3400] Packet corrupt (stream = 0, dts = NOPTS).
      Input #0, wav, from 'pipe:0':
        Duration: N/A, bitrate: 384 kb/s
        Stream #0:0: Audio: pcm_s16le ([1][0][0][0] / 0x0001), 24000 Hz, 1 channels, s16, 384 kb/s
        2.09 M-A:  0.000 fd=   0 aq=    0KB vq=    0KB sq=    0B

### 10. Kokoro — POST (your fast path) [WAV]  *Happy with results, no changes needed*
   - curl.exe -s -X POST "http://127.0.0.1:8000/synthesize/stream" -F "text=This is a streaming test." -F "engine=kokoro" -F "voice=af_heart" | ffplay -autoexit -nodisp -i pipe:0
   - Response Time: less than 1 second
   - Audo Quality: Perfect
   - Output:
     - ffplay version 7.1.1-full_build-www.gyan.dev Copyright (c) 2003-2025 the FFmpeg developers
        built with gcc 14.2.0 (Rev1, Built by MSYS2 project)
        configuration: --enable-gpl --enable-version3 --enable-static --disable-w32threads --disable-autodetect --enable-fontconfig --enable-iconv --enable-gnutls --enable-lcms2 --enable-libxml2 --enable-gmp --enable-bzlib --enable-lzma --enable-libsnappy --enable-zlib --enable-librist --enable-libsrt --enable-libssh --enable-libzmq --enable-avisynth --enable-libbluray --enable-libcaca --enable-libdvdnav --enable-libdvdread --enable-sdl2 --enable-libaribb24 --enable-libaribcaption --enable-libdav1d --enable-libdavs2 --enable-libopenjpeg --enable-libquirc --enable-libuavs3d --enable-libxevd --enable-libzvbi --enable-libqrencode --enable-librav1e --enable-libsvtav1 --enable-libvvenc --enable-libwebp --enable-libx264 --enable-libx265 --enable-libxavs2 --enable-libxeve --enable-libxvid --enable-libaom --enable-libjxl --enable-libvpx --enable-mediafoundation --enable-libass --enable-frei0r --enable-libfreetype --enable-libfribidi --enable-libharfbuzz --enable-liblensfun --enable-libvidstab --enable-libvmaf --enable-libzimg --enable-amf --enable-cuda-llvm --enable-cuvid --enable-dxva2 --enable-d3d11va --enable-d3d12va --enable-ffnvcodec --enable-libvpl --enable-nvdec --enable-nvenc --enable-vaapi --enable-libshaderc --enable-vulkan --enable-libplacebo --enable-opencl --enable-libcdio --enable-libgme --enable-libmodplug --enable-libopenmpt --enable-libopencore-amrwb --enable-libmp3lame --enable-libshine --enable-libtheora --enable-libtwolame --enable-libvo-amrwbenc --enable-libcodec2 --enable-libilbc --enable-libgsm --enable-liblc3 --enable-libopencore-amrnb --enable-libopus --enable-libspeex --enable-libvorbis --enable-ladspa --enable-libbs2b --enable-libflite --enable-libmysofa --enable-librubberband --enable-libsoxr --enable-chromaprint
        libavutil      59. 39.100 / 59. 39.100
        libavcodec     61. 19.101 / 61. 19.101
        libavformat    61.  7.100 / 61.  7.100
        libavdevice    61.  3.100 / 61.  3.100
        libavfilter    10.  4.100 / 10.  4.100
        libswscale      8.  3.100 /  8.  3.100
        libswresample   5.  3.100 /  5.  3.100
        libpostproc    58.  3.100 / 58.  3.100
      [wav @ 0000017609cb3400] Ignoring maximum wav data size, file may be invalid
      [wav @ 0000017609cb3400] Packet corrupt (stream = 0, dts = NOPTS).
      Input #0, wav, from 'pipe:0':
        Duration: N/A, bitrate: 384 kb/s
        Stream #0:0: Audio: pcm_s16le ([1][0][0][0] / 0x0001), 24000 Hz, 1 channels, s16, 384 kb/s
        2.01 M-A:  0.000 fd=   0 aq=    0KB vq=    0KB sq=    0B

# MINOR TESTING RESULTS #3a
### Cosy (WAV default)
   - curl.exe -Ns "http://127.0.0.1:8000/synthesize/stream_get?engine=cosyvoice2&cosy_mode=cross&cosy_ref_id=ref&max_chars=60&speed=1.1&text=Remote%20reference%20test" | ffplay -autoexit -nodisp -i pipe:0
   - Error Details:
      - "INFO: 127.0.0.1:61710 - "GET /synthesize/stream_get?engine=cosyvoice2&cosy_mode=cross&cosy_ref_id=ref&max_chars=60&speed=1.1&text=Remote%20reference%20test HTTP/1.1" 500 Internal Server Error ERROR: Exception in ASGI application Traceback (most recent call last): File "D:\01_Projects\Personal\tts-starter\app\services\models.py", line 186, in get_cosyvoice2 cv = CosyVoice2(root, device=device, dtype=dtype) TypeError: CosyVoice2.__init__() got an unexpected keyword argument 'device' During handling of the above exception, another exception occurred: Traceback (most recent call last): File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\uvicorn\protocols\http\httptools_impl.py", line 399, in run_asgi result = await app( # type: ignore[func-returns-value] File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\uvicorn\middleware\proxy_headers.py", line 70, in __call__ return await self.app(scope, receive, send) File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\fastapi\applications.py", line 1054, in __call__ await super().__call__(scope, receive, send) File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\starlette\applications.py", line 113, in __call__ await self.middleware_stack(scope, receive, send) File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\starlette\middleware\errors.py", line 187, in __call__ raise exc File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\starlette\middleware\errors.py", line 165, in __call__ await self.app(scope, receive, _send) File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\starlette\middleware\cors.py", line 85, in __call__ await self.app(scope, receive, send) File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\starlette\middleware\exceptions.py", line 62, in __call__ await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send) File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\starlette\_exception_handler.py", line 53, in wrapped_app raise exc File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\starlette\_exception_handler.py", line 42, in wrapped_app await app(scope, receive, sender) File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\starlette\routing.py", line 715, in __call__ await self.middleware_stack(scope, receive, send) File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\starlette\routing.py", line 735, in app await route.handle(scope, receive, send) File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\starlette\routing.py", line 288, in handle await self.app(scope, receive, send) File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\starlette\routing.py", line 76, in app await wrap_app_handling_exceptions(app, request)(scope, receive, send) File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\starlette\_exception_handler.py", line 53, in wrapped_app raise exc File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\starlette\_exception_handler.py", line 42, in wrapped_app await app(scope, receive, sender) File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\starlette\routing.py", line 73, in app response = await f(request) File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\fastapi\routing.py", line 301, in app raw_response = await run_endpoint_function( File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\fastapi\routing.py", line 214, in run_endpoint_function return await run_in_threadpool(dependant.call, **values) File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\starlette\concurrency.py", line 39, in run_in_threadpool return await anyio.to_thread.run_sync(func, *args) File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\anyio\to_thread.py", line 56, in run_sync return await get_async_backend().run_sync_in_worker_thread( File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\anyio\_backends\_asyncio.py", line 2476, in run_sync_in_worker_thread return await future File "D:\01_Projects\Personal\tts-starter\.venv\lib\site-packages\anyio\_backends\_asyncio.py", line 967, in run result = context.run(func, *args) File "D:\01_Projects\Personal\tts-starter\app\api.py", line 241, in synthesize_stream_get sr, cosy_bytes = stream_cosyvoice2_cross( File "D:\01_Projects\Personal\tts-starter\app\utils\synthesize.py", line 294, in stream_cosyvoice2_cross cv = get_cosyvoice2() # let the new policy pick CPU/GPU and FP16 File "D:\01_Projects\Personal\tts-starter\app\services\models.py", line 188, in get_cosyvoice2 cv = CosyVoice2(root) # older signature File "D:\01_Projects\Personal\tts-starter\third_party\CosyVoice\cosyvoice\cli\cosyvoice.py", line 145, in __init__ self.instruct = True if '-Instruct' in model_dir else False TypeError: argument of type 'WindowsPath' is not iterable"

### Cosy (PCM)
   - curl.exe -Ns "http://127.0.0.1:8000/synthesize/stream_get?engine=cosyvoice2&cosy_mode=cross&cosy_ref_id=ref&fmt=pcm&max_chars=60&speed=1.1&text=Remote%20reference%20test" | ffplay -autoexit -nodisp -f s16le -ar 24000 -i -
   - Error Details:
      - "ffplay version 7.1.1-full_build-www.gyan.dev Copyright (c) 2003-2025 the FFmpeg developers built with gcc 14.2.0 (Rev1, Built by MSYS2 project) configuration: --enable-gpl --enable-version3 --enable-static --disable-w32threads --disable-autodetect --enable-fontconfig --enable-iconv --enable-gnutls --enable-lcms2 --enable-libxml2 --enable-gmp --enable-bzlib --enable-lzma --enable-libsnappy --enable-zlib --enable-librist --enable-libsrt --enable-libssh --enable-libzmq --enable-avisynth --enable-libbluray --enable-libcaca --enable-libdvdnav --enable-libdvdread --enable-sdl2 --enable-libaribb24 --enable-libaribcaption --enable-libdav1d --enable-libdavs2 --enable-libopenjpeg --enable-libquirc --enable-libuavs3d --enable-libxevd --enable-libzvbi --enable-libqrencode --enable-librav1e --enable-libsvtav1 --enable-libvvenc --enable-libwebp --enable-libx264 --enable-libx265 --enable-libxavs2 --enable-libxeve --enable-libxvid --enable-libaom --enable-libjxl --enable-libvpx --enable-mediafoundation --enable-libass --enable-frei0r --enable-libfreetype --enable-libfribidi --enable-libharfbuzz --enable-liblensfun --enable-libvidstab --enable-libvmaf --enable-libzimg --enable-amf --enable-cuda-llvm --enable-cuvid --enable-dxva2 --enable-d3d11va --enable-d3d12va --enable-ffnvcodec --enable-libvpl --enable-nvdec --enable-nvenc --enable-vaapi --enable-libshaderc --enable-vulkan --enable-libplacebo --enable-opencl --enable-libcdio --enable-libgme --enable-libmodplug --enable-libopenmpt --enable-libopencore-amrwb --enable-libmp3lame --enable-libshine --enable-libtheora --enable-libtwolame --enable-libvo-amrwbenc --enable-libcodec2 --enable-libilbc --enable-libgsm --enable-liblc3 --enable-libopencore-amrnb --enable-libopus --enable-libspeex --enable-libvorbis --enable-ladspa --enable-libbs2b --enable-libflite --enable-libmysofa --enable-librubberband --enable-libsoxr --enable-chromaprint libavutil 59. 39.100 / 59. 39.100 libavcodec 61. 19.101 / 61. 19.101 libavformat 61. 7.100 / 61. 7.100 libavdevice 61. 3.100 / 61. 3.100 libavfilter 10. 4.100 / 10. 4.100 libswscale 8. 3.100 / 8. 3.100 libswresample 5. 3.100 / 5. 3.100 libpostproc 58. 3.100 / 58. 3.100 Input #0, s16le, from 'fd:':aq= 0KB vq= 0KB sq= 0B Duration: N/A, bitrate: 384 kb/s Stream #0:0: Audio: pcm_s16le, 24000 Hz, mono, s16, 384 kb/s [pcm_s16le @ 000001dafef87540] Invalid PCM packet, data has size 1 but at least a size of 2 was expected nan M-A: nan fd= 0 aq= 0KB vq= 0KB sq= 0B"

### Kokoro (PCM GET)
   - curl.exe -Ns "http://127.0.0.1:8000/synthesize/stream_get?engine=kokoro&voice=af_heart&fmt=pcm&max_chars=100&text=Hello%20from%20the%20GET%20stream" | ffplay -autoexit -nodisp -f s16le -ar 24000 -i pipe:0
   - Error Details: None worked and sounded perfect
      - 

# TESTING RESULTS #4

### 1. CosyVoice2 (preset ref id)
   - curl.exe -Ns "http://127.0.0.1:8000/synthesize/stream_get?engine=cosyvoice2&cosy_mode=cross&cosy_ref_id=ref&max_chars=60&speed=1.1&text=Remote%20reference%20test" | ffplay -autoexit -nodisp -i pipe:0 
   - Response Time: 
   - Audo Quality: 
   - Output:
     - 
   - Error Details:
     - 

### 2. CosyVoice2 (remote ref URL)
   - $ref = [uri]::EscapeDataString("https://samplelib.com/lib/preview/wav/sample-3s.wav")
   - curl.exe -Ns "http://127.0.0.1:8000/synthesize/stream_get?engine=cosyvoice2&cosy_mode=cross&cosy_ref_url=$ref&max_chars=60&speed=1.1&text=Remote%20reference%20test" | ffplay -autoexit -nodisp -i pipe:0 
   - Response Time: 
   - Audo Quality: 
   - Output:
     - 
   - Error Details:
     - 

### 3. Kokoro — GET *Happy with results, no changes needed*
   - curl.exe -Ns "http://127.0.0.1:8000/synthesize/stream_get?engine=kokoro&voice=af_heart&max_chars=100&text=Hello%20from%20the%20GET%20stream" | ffplay -autoexit -nodisp -i pipe:0 
   - Response Time: 
   - Audo Quality: 
   - Output:
     -  

### 4. Kokoro — POST *Happy with results, no changes needed*
   - curl.exe -s -X POST "http://127.0.0.1:8000/synthesize/stream" -F "text=This is a streaming test." -F "engine=kokoro" -F "voice=af_heart" | ffplay -autoexit -nodisp -i pipe:0 
   - Response Time: 
   - Audo Quality: 
   - Output:
     - 

### 5. Cosy PCM — lower latency, no warnings
   - curl.exe -Ns "http://127.0.0.1:8000/synthesize/stream_get?engine=cosyvoice2&cosy_mode=cross&cosy_ref_id=ref&fmt=pcm&max_chars=60&speed=1.1&text=Remote%20reference%20test" | ffplay -autoexit -nodisp -f s16le -ar 24000 -ac 1 -i -
   - Response Time: 
   - Audo Quality: 
   - Output:
     - 
   - Error Details: 
     - 

### 6. Cosy WAV - current default
   - curl.exe -Ns "http://127.0.0.1:8000/synthesize/stream_get?engine=cosyvoice2&cosy_mode=cross&cosy_ref_id=ref&max_chars=60&speed=1.1&text=Remote%20reference%20test" | ffplay -autoexit -nodisp -i pipe:0
   - Response Time: 
   - Audo Quality: 
   - Output:
     - 
   - Error Details:
     - 

### 7. Kokoro - GET (PCM)
   - curl.exe -Ns "http://127.0.0.1:8000/synthesize/stream_get?engine=kokoro&voice=af_heart&fmt=pcm&max_chars=100&text=Hello%20from%20the%20GET%20stream" | ffplay -autoexit -nodisp -f s16le -ar 24000 -i pipe:0
   - Response Time: 
   - Audo Quality: 
   - Output:
     - 
   - Error Details:
    - 

### 8. Kokoro - GET (WAV)  *Happy with results, no changes needed*
   - curl.exe -Ns "http://127.0.0.1:8000/synthesize/stream_get?engine=kokoro&voice=af_heart&max_chars=100&text=Hello%20from%20the%20GET%20stream" | ffplay -autoexit -nodisp -i pipe:0
   - Response Time: 
   - Audo Quality: Prfect
   - Output:
     - 

### 9. Kokoro — POST (your fast path) [PCM]  *Happy with results, no changes needed*
   - curl.exe -s -X POST "http://127.0.0.1:8000/synthesize/stream" -F "text=This is a streaming test." -F "engine=kokoro" -F "voice=af_heart" -F "fmt=pcm" | ffplay -autoexit -nodisp -f s16le -ar 24000 -ac 1 -i pipe:0
   - Response Time: 
   - Audo Quality: 
   - Output:
     - 

### 10. Kokoro — POST (your fast path) [WAV]  *Happy with results, no changes needed*
   - curl.exe -s -X POST "http://127.0.0.1:8000/synthesize/stream" -F "text=This is a streaming test." -F "engine=kokoro" -F "voice=af_heart" | ffplay -autoexit -nodisp -i pipe:0
   - Response Time: 
   - Audo Quality: 
   - Output:
     - 

---

# WORKING AREA

curl.exe -Ns "http://127.0.0.1:8000/synthesize/stream_get?engine=cosyvoice2&cosy_mode=cross&cosy_ref_id=ref&max_chars=60&speed=1.1&text=Remote%20reference%20test" | ffplay -autoexit -nodisp -i pipe:0

curl.exe -Ns "http://127.0.0.1:8000/synthesize/stream_get?engine=cosyvoice2&cosy_mode=cross&cosy_ref_id=ref&fmt=pcm&max_chars=60&speed=1.1&text=Remote%20reference%20test" | ffplay -autoexit -nodisp -f s16le -ar 24000 -i -

curl.exe -Ns "http://127.0.0.1:8000/synthesize/stream_get?engine=cosyvoice2&cosy_mode=cross&cosy_ref_id=ref&fmt=pcm&max_chars=60&speed=1.1&text=Remote%20reference%20test" | ffplay -autoexit -nodisp -f s16le -ar 24000 -i pipe:0

# PCM from CosyVoice2 [-ac might not work]
curl.exe -Ns "http://127.0.0.1:8000/synthesize/stream_get?engine=cosyvoice2&cosy_mode=cross&cosy_ref_id=ref&fmt=pcm&max_chars=60&speed=1.1&text=Remote%20reference%20test" | ffplay -autoexit -nodisp -f s16le -ar 24000 -ac 1 -i pipe:0










# RETEST COMMANDS
curl.exe -Ns "http://127.0.0.1:8000/synthesize/stream_get?engine=cosyvoice2&cosy_mode=cross&cosy_ref_id=ref&max_chars=60&speed=1.1&text=Remote%20reference%20test" | ffplay -autoexit -nodisp -i pipe:0

curl.exe -Ns "http://127.0.0.1:8000/synthesize/stream_get?engine=cosyvoice2&cosy_mode=cross&cosy_ref_id=ref&max_chars=60&speed=1.1&text=Remote%20reference%20test" | ffplay -autoexit -nodisp -i pipe:0

tar -czf tts-review-core.tgz app third_party/CosyVoice/cosyvoice/cli third_party/CosyVoice/cosyvoice/modules third_party/CosyVoice/cosyvoice/utils data/refs requirements.txt pyproject.toml poetry.lock Dockerfile .env.example --exclude='.git' --exclude='.venv' --exclude='__pycache__' --exclude='*.pth' --exclude='*.pt' --exclude='*.bin' --exclude='*.safetensors' --exclude='*.onnx' --exclude='*.gguf' --exclude='*.tflite' --exclude='checkpoints' --exclude='pretrained*' --exclude='models'
