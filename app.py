import streamlit as st
import yt_dlp
import tempfile
import os
import shutil

# --- Streamlit page config ---
st.set_page_config(
    page_title="YouTube Downloader",
    page_icon="📥",
    layout="centered"
)

# --- Custom CSS for style ---
st.markdown("""
    <style>
    .stApp {
        background-color: #f0f2f6;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        font-size: 16px;
        padding: 10px 24px;
        border-radius: 5px;
    }
    .stButton>button:hover {
        background-color: #45a049;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# --- App title and description ---
st.title("📥 YouTube Downloader")
st.markdown("Download YouTube videos in **MP4** or **MP3** format directly from your browser!")

# --- Input URL ---
video_url = st.text_input("Enter YouTube URL:")

if video_url:
    # Fetch formats
    try:
        st.info("Fetching video information...")
        ydl_opts = {"quiet": True, "noplaylist": True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            title = info.get("title", "Unknown Title")
            formats = info.get("formats", [])

            # Build list for display
            format_list = []
            for f in formats:
                if f.get("acodec") != "none" or f.get("vcodec") != "none":
                    desc = f"{f.get('format_id')} | {f.get('ext')} | {f.get('resolution','audio')} | {f.get('acodec')}/{f.get('vcodec')}"
                    format_list.append((f.get("format_id"), desc))
        st.success(f"Video: **{title}** fetched successfully!")
    except Exception as e:
        st.error(f"Failed to fetch video: {e}")
        format_list = []

    # Download options
    kind = st.radio("Download type:", ["MP4 (video)", "MP3 (audio)"])
    if kind == "MP4 (video)" and format_list:
        format_choice = st.selectbox("Select video format:", [desc for _, desc in format_list])
        format_id = next(fid for fid, desc in format_list if desc == format_choice)
    else:
        format_id = None

    if st.button("Download"):
        try:
            tempdir = tempfile.mkdtemp()
            outtmpl = os.path.join(tempdir, "%(title)s.%(ext)s")

            if kind == "MP4 (video)":
                ydl_opts = {
                    "format": format_id or "bestvideo+bestaudio/best",
                    "outtmpl": outtmpl,
                    "noplaylist": True,
                    "quiet": True,
                    "merge_output_format": "mp4",
                    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36"
                }
            else:  # MP3 download
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
                    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36"
                }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.extract_info(video_url, download=True)

            # Find downloaded file
            files = [os.path.join(tempdir, f) for f in os.listdir(tempdir)]
            if not files:
                st.error("No file downloaded.")
            else:
                file_path = files[0]
                file_name = os.path.basename(file_path)
                st.success(f"✅ Download complete: {file_name}")
                with open(file_path, "rb") as f:
                    st.download_button("Click to download", f, file_name)

            # Cleanup
            shutil.rmtree(tempdir)
        except Exception as e:
            st.error(f"Download failed: {e}")
