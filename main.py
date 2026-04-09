import streamlit as st
import pandas as pd
import re
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

st.set_page_config(
    page_title="유튜브 댓글 수집기",
    page_icon="💬",
    layout="wide"
)

st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #16213e 100%);
    }
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
        border-right: 1px solid rgba(255,255,255,0.05);
    }
    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] .stMarkdown h3 {
        color: #e0e0e0 !important;
    }
    .hero-container {
        text-align: center;
        padding: 2rem 1rem 1rem 1rem;
    }
    .hero-icon { font-size: 3rem; margin-bottom: 0.5rem; }
    .hero-title {
        font-size: 2rem;
        font-weight: 700;
        background: linear-gradient(90deg, #a78bfa, #60a5fa, #34d399);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.3rem;
    }
    .hero-subtitle {
        font-size: 0.95rem;
        color: #94a3b8;
        margin-bottom: 1.5rem;
    }
    .glass-card {
        background: rgba(255, 255, 255, 0.04);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
    .video-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #e2e8f0;
        margin-bottom: 0.5rem;
        line-height: 1.5;
    }
    .video-meta {
        font-size: 0.85rem;
        color: #94a3b8;
        margin-bottom: 0.3rem;
    }
    .stat-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 12px;
        margin-top: 1rem;
    }
    .stat-item {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
    }
    .stat-value {
        font-size: 1.3rem;
        font-weight: 700;
        color: #e2e8f0;
    }
    .stat-label {
        font-size: 0.75rem;
        color: #64748b;
        margin-top: 0.2rem;
    }
    .comment-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 12px;
        padding: 1rem 1.2rem;
        margin-bottom: 8px;
        transition: all 0.2s ease;
    }
    .comment-card:hover {
        background: rgba(255, 255, 255, 0.06);
        border-color: rgba(167, 139, 250, 0.3);
    }
    .comment-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.5rem;
    }
    .comment-author {
        font-weight: 600;
        font-size: 0.9rem;
        color: #a78bfa;
    }
    .comment-date {
        font-size: 0.75rem;
        color: #64748b;
    }
    .comment-body {
        font-size: 0.9rem;
        color: #cbd5e1;
        line-height: 1.6;
        margin-bottom: 0.5rem;
    }
    .comment-likes {
        font-size: 0.8rem;
        color: #64748b;
    }
    .comment-likes span {
        color: #f472b6;
        font-weight: 600;
    }
    .reply-badge {
        display: inline-block;
        background: rgba(96, 165, 250, 0.15);
        color: #60a5fa;
        font-size: 0.7rem;
        padding: 2px 8px;
        border-radius: 20px;
        margin-right: 6px;
    }
    .success-banner {
        background: linear-gradient(90deg, rgba(52, 211, 153, 0.1), rgba(96, 165, 250, 0.1));
        border: 1px solid rgba(52, 211, 153, 0.2);
        border-radius: 12px;
        padding: 1rem 1.5rem;
        text-align: center;
        color: #34d399;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    .section-title {
        font-size: 1.2rem;
        font-weight: 600;
        color: #e2e8f0;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid rgba(255,255,255,0.06);
    }
    .divider {
        border: none;
        border-top: 1px solid rgba(255,255,255,0.06);
        margin: 1.5rem 0;
    }
    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 10px !important;
        color: #e2e8f0 !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: rgba(167, 139, 250, 0.5) !important;
        box-shadow: 0 0 0 1px rgba(167, 139, 250, 0.3) !important;
    }
    .stSelectbox > div > div {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 10px !important;
    }
    .stButton > button {
        background: linear-gradient(90deg, #7c3aed, #6366f1) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.6rem 2rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    .stButton > button:hover {
        background: linear-gradient(90deg, #6d28d9, #4f46e5) !important;
        box-shadow: 0 4px 20px rgba(124, 58, 237, 0.4) !important;
    }
    .stDownloadButton > button {
        background: linear-gradient(90deg, #059669, #0d9488) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
    }
    .stDownloadButton > button:hover {
        background: linear-gradient(90deg, #047857, #0f766e) !important;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: rgba(255,255,255,0.03);
        border-radius: 12px;
        padding: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        color: #94a3b8;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background: rgba(167, 139, 250, 0.15) !important;
        color: #a78bfa !important;
    }
    [data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 12px;
        padding: 1rem;
    }
    [data-testid="stMetricLabel"] { color: #64748b !important; }
    [data-testid="stMetricValue"] { color: #e2e8f0 !important; }
</style>
""", unsafe_allow_html=True)


def get_api_key():
    try:
        api_key = st.secrets["YOUTUBE_API_KEY"]
        if api_key:
            return api_key
    except (KeyError, FileNotFoundError):
        pass

    st.sidebar.markdown("### 🔑 API 키 설정")
    st.sidebar.markdown("YouTube Data API v3 키를 입력하세요.")
    st.sidebar.markdown("[📘 API 키 발급 방법 안내](https://console.cloud.google.com/apis/library/youtube.googleapis.com)")
    api_key = st.sidebar.text_input(
        "YouTube API Key",
        type="password",
        placeholder="AIza..."
    )
    return api_key if api_key else None


def extract_video_id(url):
    """다양한 유튜브 URL 형식에서 video ID 추출"""
    url = url.strip()

    patterns = [
        r'(?:v=)([a-zA-Z0-9_-]{11})',
        r'(?:youtu\.be/)([a-zA-Z0-9_-]{11})',
        r'(?:embed/)([a-zA-Z0-9_-]{11})',
        r'(?:shorts/)([a-zA-Z0-9_-]{11})',
        r'^([a-zA-Z0-9_-]{11})$',
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def get_video_info(youtube, video_id):
    """비디오 정보 가져오기 - 에러 상세 표시"""
    try:
        response = youtube.videos().list(
            part="snippet,statistics",
            id=video_id
        ).execute()

        # 응답에 아이템이 없는 경우
        if not response.get("items"):
            st.error(f"❌ 비디오 ID `{video_id}`에 해당하는 영상을 찾을 수 없습니다.")
            st.info("💡 URL을 다시 확인해주세요. 비공개/삭제된 영상일 수도 있습니다.")
            return None

        item = response["items"][0]
        snippet = item["snippet"]
        stats = item["statistics"]
        return {
            "title": snippet.get("title", ""),
            "channel": snippet.get("channelTitle", ""),
            "published": snippet.get("publishedAt", "")[:10],
            "thumbnail": snippet.get("thumbnails", {}).get("high", {}).get("url", ""),
            "view_count": int(stats.get("viewCount", 0)),
            "like_count": int(stats.get("likeCount", 0)),
            "comment_count": int(stats.get("commentCount", 0)),
        }

    except HttpError as e:
        error_reason = ""
        try:
            import json
            error_detail = json.loads(e.content.decode("utf-8"))
            error_reason = error_detail["error"]["errors"][0]["reason"]
            error_message = error_detail["error"]["errors"][0]["message"]
        except Exception:
            error_reason = "unknown"
            error_message = str(e)

        if error_reason == "keyInvalid":
            st.error("❌ API 키가 유효하지 않습니다.")
            st.info("💡 Google Cloud Console에서 API 키를 다시 확인해주세요.")
        elif error_reason == "accessNotConfigured":
            st.error("❌ YouTube Data API v3가 활성화되지 않았습니다.")
            st.info("💡 Google Cloud Console → API 및 서비스 → 라이브러리에서 YouTube Data API v3를 '사용' 설정해주세요.")
        elif error_reason == "quotaExceeded":
            st.error("❌ API 일일 할당량을 초과했습니다.")
            st.info("💡 내일 다시 시도하거나 Google Cloud Console에서 할당량을 확인하세요.")
        elif error_reason == "forbidden":
            st.error("❌ API 접근이 거부되었습니다.")
            st.info("💡 API 키 제한 설정을 확인해주세요. 처음에는 '제한 없음'으로 설정하는 것을 추천합니다.")
        else:
            st.error(f"❌ API 오류 발생: {error_reason}")
            st.code(error_message)

        return None

    except Exception as e:
        st.error(f"❌ 예상치 못한 오류: {type(e).__name__}")
        st.code(str(e))
        return None


def get_comments(youtube, video_id, max_comments=100):
    comments = []
    next_page_token = None
    try:
        while len(comments) < max_comments:
            response = youtube.commentThreads().list(
                part="snippet,replies",
                videoId=video_id,
                maxResults=min(100, max_comments - len(comments)),
                pageToken=next_page_token,
                textFormat="plainText",
                order="relevance"
            ).execute()
            for item in response.get("items", []):
                top = item["snippet"]["topLevelComment"]["snippet"]
                comments.append({
                    "작성자": top.get("authorDisplayName", ""),
                    "댓글": top.get("textDisplay", ""),
                    "좋아요": top.get("likeCount", 0),
                    "작성일": top.get("publishedAt", "")[:10],
                    "유형": "댓글"
                })
                if item.get("replies"):
                    for reply_item in item["replies"]["comments"]:
                        reply = reply_item["snippet"]
                        comments.append({
                            "작성자": reply.get("authorDisplayName", ""),
                            "댓글": reply.get("textDisplay", ""),
                            "좋아요": reply.get("likeCount", 0),
                            "작성일": reply.get("publishedAt", "")[:10],
                            "유형": "답글"
                        })
                if len(comments) >= max_comments:
                    break
            next_page_token = response.get("nextPageToken")
            if not next_page_token:
                break

    except HttpError as e:
        try:
            import json
            error_detail = json.loads(e.content.decode("utf-8"))
            error_reason = error_detail["error"]["errors"][0]["reason"]
        except Exception:
            error_reason = "unknown"

        if error_reason == "commentsDisabled":
            st.error("❌ 이 영상은 댓글이 비활성화되어 있습니다.")
        elif error_reason == "quotaExceeded":
            st.warning("⚠️ API 할당량 초과. 지금까지 수집된 댓글만 표시합니다.")
        else:
            st.error(f"❌ 댓글 수집 중 오류: {error_reason}")

    return comments[:max_comments]


def format_number(n):
    if n >= 100000000:
        return f"{n / 100000000:.1f}억"
    elif n >= 10000:
        return f"{n / 10000:.1f}만"
    elif n >= 1000:
        return f"{n / 1000:.1f}천"
    return f"{n:,}"


def main():
    st.markdown("""
    <div class="hero-container">
        <div class="hero-icon">💬</div>
        <div class="hero-title">YouTube Comment Collector</div>
        <div class="hero-subtitle">유튜브 영상 링크를 입력하면 댓글을 수집하고 분석합니다</div>
    </div>
    """, unsafe_allow_html=True)

    api_key = get_api_key()

    if not api_key:
        st.info("👈 사이드바에서 YouTube API 키를 입력해주세요.")
        st.markdown("""
        <div class="glass-card">
            <div class="section-title">📌 YouTube Data API 키 발급 방법</div>
            <div style="color: #94a3b8; line-height: 2;">
                1️⃣ <a href="https://console.cloud.google.com/" style="color: #60a5fa;">Google Cloud Console</a> 접속<br>
                2️⃣ 새 프로젝트 생성<br>
                3️⃣ API 및 서비스 → 라이브러리 → YouTube Data API v3 사용 설정<br>
                4️⃣ 사용자 인증 정보 → API 키 만들기<br>
                5️⃣ 생성된 키를 사이드바에 붙여넣기
            </div>
        </div>
        """, unsafe_allow_html=True)
        return

    youtube = build("youtube", "v3", developerKey=api_key)

    # API 키 유효성 간단 테스트
    st.sidebar.markdown("---")
    if st.sidebar.button("🔍 API 키 테스트"):
        try:
            test = youtube.videos().list(part="snippet", id="dQw4w9WgXcQ").execute()
            if test.get("items"):
                st.sidebar.success("✅ API 키가 정상 작동합니다!")
            else:
                st.sidebar.error("❌ 응답은 왔지만 데이터가 없습니다.")
        except HttpError as e:
            st.sidebar.error(f"❌ API 오류: {e.resp.status}")
            try:
                import json
                detail = json.loads(e.content.decode("utf-8"))
                reason = detail["error"]["errors"][0]["reason"]
                msg = detail["error"]["errors"][0]["message"]
                st.sidebar.error(f"원인: {reason}")
                st.sidebar.code(msg)
            except Exception:
                st.sidebar.code(str(e))
        except Exception as e:
            st.sidebar.error(f"❌ 오류: {e}")

    # 입력 영역
    col_input, col_option = st.columns([4, 1])
    with col_input:
        url = st.text_input(
            "🔗 유튜브 영상 URL",
            placeholder="https://www.youtube.com/watch?v=..."
        )
    with col_option:
        max_comments = st.selectbox(
            "수집 수",
            options=[50, 100, 200, 300, 500],
            index=1
        )

    # URL 입력 시 추출된 ID 미리보기
    if url:
        vid = extract_video_id(url)
        if vid:
            st.caption(f"📎 감지된 Video ID: `{vid}`")
        else:
            st.caption("⚠️ Video ID를 추출할 수 없습니다. URL을 확인해주세요.")

    search_button = st.button("💬 댓글 수집 시작", use_container_width=True)

    if search_button and url:
        video_id = extract_video_id(url)
        if not video_id:
            st.error("올바른 유튜브 URL을 입력해주세요.")
            return

        with st.spinner("영상 정보를 불러오는 중..."):
            video_info = get_video_info(youtube, video_id)

        if not video_info:
            return

        st.markdown('<hr class="divider">', unsafe_allow_html=True)

        col_thumb, col_info = st.columns([1, 2.5])
        with col_thumb:
            if video_info["thumbnail"]:
                st.image(video_info["thumbnail"], use_container_width=True)
        with col_info:
            st.markdown(f"""
            <div class="video-title">{video_info['title']}</div>
            <div class="video-meta">📢 {video_info['channel']}　·　📅 {video_info['published']}</div>
            <div class="stat-grid">
                <div class="stat-item">
                    <div class="stat-value">{format_number(video_info['view_count'])}</div>
                    <div class="stat-label">조회수</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{format_number(video_info['like_count'])}</div>
                    <div class="stat-label">좋아요</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{format_number(video_info['comment_count'])}</div>
                    <div class="stat-label">댓글</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('<hr class="divider">', unsafe_allow_html=True)

        with st.spinner(f"댓글을 수집하는 중... (최대 {max_comments}개)"):
            comments = get_comments(youtube, video_id, max_comments)

        if not comments:
            st.info("수집된 댓글이 없습니다.")
            return

        st.markdown(
            f'<div class="success-banner">✅ 총 {len(comments)}개 댓글을 수집했습니다</div>',
            unsafe_allow_html=True
        )

        df = pd.DataFrame(comments)

        tab1, tab2, tab3 = st.tabs(["💬 댓글 보기", "📊 테이블", "📈 통계"])

        with tab1:
            search_keyword = st.text_input(
                "검색",
                placeholder="🔎 댓글 내 키워드 검색...",
                label_visibility="collapsed"
            )
            display_df = df.copy()
            if search_keyword:
                display_df = display_df[
                    display_df["댓글"].str.contains(search_keyword, case=False, na=False)
                ]
                st.markdown(
                    f'<div style="color:#60a5fa; font-size:0.85rem; margin-bottom:1rem;">'
                    f'"{search_keyword}" 검색 결과: {len(display_df)}개</div>',
                    unsafe_allow_html=True
                )

            for _, row in display_df.iterrows():
                reply_badge = '<span class="reply-badge">답글</span>' if row["유형"] == "답글" else ""
                comment_text = row["댓글"].replace("<", "&lt;").replace(">", "&gt;")
                author_text = row["작성자"].replace("<", "&lt;").replace(">", "&gt;")
                st.markdown(f"""
                <div class="comment-card">
                    <div class="comment-header">
                        <div class="comment-author">{reply_badge}{author_text}</div>
                        <div class="comment-date">{row['작성일']}</div>
                    </div>
                    <div class="comment-body">{comment_text}</div>
                    <div class="comment-likes">♥ <span>{row['좋아요']}</span></div>
                </div>
                """, unsafe_allow_html=True)

        with tab2:
            st.dataframe(
                df,
                use_container_width=True,
                height=500,
                column_config={
                    "좋아요": st.column_config.NumberColumn("♥ 좋아요", format="%d"),
                    "작성일": st.column_config.TextColumn("📅 작성일"),
                }
            )

        with tab3:
            top_comments = df[df["유형"] == "댓글"]
            reply_comments = df[df["유형"] == "답글"]
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("전체 수집", f"{len(df)}개")
            c2.metric("댓글", f"{len(top_comments)}개")
            c3.metric("답글", f"{len(reply_comments)}개")
            c4.metric("좋아요 합계", f"{df['좋아요'].sum():,}")

            st.markdown('<div class="section-title">🏆 좋아요 TOP 10</div>', unsafe_allow_html=True)
            top10 = df.nlargest(10, "좋아요")[["작성자", "댓글", "좋아요", "작성일"]]
            st.dataframe(top10, use_container_width=True, hide_index=True)

        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        csv_data = df.to_csv(index=False, encoding="utf-8-sig")
        st.download_button(
            label="📥 CSV 파일 다운로드",
            data=csv_data,
            file_name=f"youtube_comments_{video_id}.csv",
            mime="text/csv",
            use_container_width=True
        )

    elif search_button and not url:
        st.warning("유튜브 URL을 입력해주세요.")


if __name__ == "__main__":
    main()
