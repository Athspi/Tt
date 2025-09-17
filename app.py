import streamlit as st
import yt_dlp
import os
import tempfile

st.set_page_config(page_title="YouTube Downloader", page_icon="📥")

st.title("📥 YouTube Downloader (MP4/MP3)")

# Input URL
video_url = st.text_input("Enter YouTube URL:")

if video_url:
    st.info("Fetching available formats...")
    try:
        # List formats
        with yt_dlp.YoutubeDL({}) as ydl:
            info = ydl.extract_info(video_url, download=False)
            formats = info.get("formats", [])
            
            format_list = []
            for f in formats:
                # only video/audio formats
                if f.get("acodec") != "none" or f.get("vcodec") != "none":
                    desc = f"{f.get('format_id')} | {f.get('ext')} | {f.get('resolution','audio')} | {f.get('acodec')}/{f.get('vcodec')}"
                    format_list.append((f.get('format_id'), desc))
            
            st.success("Formats fetched successfully!")
    except Exception as e:
        st.error(f"Error fetching formats: {e}")
        format_list = []

    # User options
    kind = st.radio("Download type:", ["MP4 (video)", "MP3 (audio)"])

    if kind == "MP4 (video)" and format_list:
        format_choice = st.selectbox("Select format:", [desc for _, desc in format_list])
        # map back to format_id
        format_id = next(fid for fid, desc in format_list if desc == format_choice)
    else:
        format_id = None  # mp3 uses bestaudio by default

    if st.button("Download"):
        try:
            tempdir = tempfile.mkdtemp()
            outtmpl = os.path.join(tempdir, "%(title)s.%(ext)s")
            
            if kind == "MP4 (video)":
                ydl_opts = {
                    "format": format_id or "bestvideo+bestaudio/best",
                    "outtmpl": outtmpl,
                    "noplaylist": True,
                    "quiet": True
                }
            else:
                ydl_opts = {
                    "format": "bestaudio/best",
                    "outtmpl": outtmpl,
                    "noplaylist": True,
                    "quiet": True,
                    "postprocessors": [{
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192",
                    }],
                }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=True)
            
            # find downloaded file
            files = [os.path.join(tempdir, f) for f in os.listdir(tempdir)]
            if not files:
                st.error("No file downloaded.")
            else:
                file_path = files[0]
                file_name = os.path.basename(file_path)
                st.success(f"✅ Download complete: {file_name}")
                with open(file_path, "rb") as f:
                    st.download_button("Click to download", f, file_name)
        except Exception as e:
            st.error(f"Download failed: {e}")
