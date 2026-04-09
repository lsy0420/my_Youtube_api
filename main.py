import streamlit as st
import pandas as pd
import re
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

st.set_page_config(
    page_title="유튜브 댓글 수집기",
    page_icon="📺",
    layout="wide"
)

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        color: #FF0000;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .comment-box {
        background-color: #f9f9f9;
        border-left: 4px solid #FF0000;
        padding: 12px 16px;
        margin-bottom: 10px;
        border-radius: 4px;
    }
    .comment-author {
        font-weight: bold;
        color: #333;
        margin-bottom: 4px;
    }
    .comment-text {
        color: #555;
        line-height: 1.6;
    }
    .comment-meta {
        color: #999;
        font-size: 0.8rem;
        margin-top: 4px;
    }
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
    st.sidebar.markdown(
        "YouTube Data API v3 키를 입력하세요.\n\n"
        "[API 키 발급 방법 안내](https://console.cloud.google.com/apis/library/youtube.googleapis.com)"
    )
    api_key = st.sidebar.text_input(
        "YouTube API Key",
        type="password",
        placeholder="AIza..."
    )
    return api_key if api_key else None


def extract_video_id(url):
    patterns = [
        r'(?:v=)([a-zA-Z0-9_-]{11})',
        r'(?:youtu\.be/)([a-zA-Z0-9_-]{11})',
        r'(?:embed/)([a-zA-Z0-9_-]{11})',
        r'(?:shorts/)([a-zA-Z0-9_-]{11})',
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def get_video_info(youtube, video_id):
    try:
        response = youtube.videos().list(
            part="snippet,statistics",
            id=video_id
        ).execute()

        if response["items"]:
            item = response["items"][0]
            snippet = item["snippet"]
            stats = item["statistics"]
            return {
                "title": snippet.get("title", "제목 없음"),
                "channel": snippet.get("channelTitle", "알 수 없음"),
                "published": snippet.get("publishedAt", "")[:10],
                "thumbnail": snippet.get("thumbnails", {}).get("high", {}).get("url", ""),
                "view_count": int(stats.get("viewCount", 0)),
                "like_count": int(stats.get("likeCount", 0)),
                "comment_count": int(stats.get("commentCount", 0)),
            }
    except HttpError:
        return None
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
                            "유형": "↳ 답글"
                        })

                if len(comments) >= max_comments:
                    break

            next_page_token = response.get("nextPageToken")
            if not next_page_token:
                break

    except HttpError as e:
        if e.resp.status == 403:
            st.error("⚠️ 댓글이 비활성화된 영상이거나 API 할당량을 초과했습니다.")
        else:
            st.error(f"⚠️ API 오류가 발생했습니다: {e}")
        return comments

    return comments[:max_comments]


def main():
    st.markdown('<div class="main-header">📺 유튜브 댓글 수집기</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">유튜브 영상 링크를 입력하면 댓글을 수집하고 분석합니다</div>', unsafe_allow_html=True)

    api_key = get_api_key()

    if not api_key:
        st.warning("⬅️ 사이드바에서 YouTube API 키를 입력해주세요.")
        st.markdown("---")
        st.markdown("""
        ### 📌 YouTube Data API 키 발급 방법
        1. [Google Cloud Console](https://console.cloud.google.com/) 접속
        2. 새 프로젝트 생성
        3. **API 및 서비스 → 라이브러리** → **YouTube Data API v3** 사용 설정
        4. **사용자 인증 정보 → API 키 만들기**
        5. 생성된 키를 사이드바에 붙여넣기
        """)
        return

    youtube = build("youtube", "v3", developerKey=api_key)

    st.markdown("---")
    col_input, col_option = st.columns([3, 1])

    with col_input:
        url = st.text_input(
            "🔗 유튜브 영상 URL",
            placeholder="https://www.youtube.com/watch?v=..."
        )

    with col_option:
        max_comments = st.selectbox(
            "📊 최대 수집 수",
            options=[50, 100, 200, 300, 500],
            index=1
        )

    search_button = st.button("🔍 댓글 수집 시작", use_container_width=True, type="primary")

    if search_button and url:
        video_id = extract_video_id(url)

        if not video_id:
            st.error("❌ 올바른 유튜브 URL을 입력해주세요.")
            return

        with st.spinner("영상 정보를 불러오는 중..."):
            video_info = get_video_info(youtube, video_id)

        if not video_info:
            st.error("❌ 영상 정보를 가져올 수 없습니다.")
            return

        st.markdown("---")
        st.markdown("### 🎬 영상 정보")

        col_thumb, col_info = st.columns([1, 2])
        with col_thumb:
            if video_info["thumbnail"]:
                st.image(video_info["thumbnail"], use_container_width=True)
        with col_info:
            st.markdown(f"**{video_info['title']}**")
            st.markdown(f"📢 채널: {video_info['channel']}")
            st.markdown(f"📅 게시일: {video_info['published']}")

            mc1, mc2, mc3 = st.columns(3)
            mc1.metric("👀 조회수", f"{video_info['view_count']:,}")
            mc2.metric("👍 좋아요", f"{video_info['like_count']:,}")
            mc3.metric("💬 댓글 수", f"{video_info['comment_count']:,}")

        st.markdown("---")
        st.markdown("### 💬 댓글 목록")

        with st.spinner(f"댓글을 수집하는 중... (최대 {max_comments}개)"):
            comments = get_comments(youtube, video_id, max_comments)

        if not comments:
            st.info("수집된 댓글이 없습니다.")
            return

        st.success(f"✅ 총 **{len(comments)}개** 댓글을 수집했습니다!")

        df = pd.DataFrame(comments)

        tab1, tab2, tab3 = st.tabs(["📋 카드 보기", "📊 테이블 보기", "📈 간단 통계"])

        with tab1:
            search_keyword = st.text_input("🔎 댓글 내 키워드 검색", placeholder="검색어를 입력하세요...")
            display_df = df.copy()
            if search_keyword:
                display_df = display_df[
                    display_df["댓글"].str.contains(search_keyword, case=False, na=False)
                ]
                st.info(f"'{search_keyword}' 검색 결과: {len(display_df)}개")

            for _, row in display_df.iterrows():
                st.markdown(f"""
                <div class="comment-box">
                    <div class="comment-author">{row['유형']} {row['작성자']}</div>
                    <div class="comment-text">{row['댓글']}</div>
                    <div class="comment-meta">👍 {row['좋아요']}  ·  📅 {row['작성일']}</div>
                </div>
                """, unsafe_allow_html=True)

        with tab2:
            st.dataframe(
                df,
                use_container_width=True,
                height=500,
                column_config={
                    "좋아요": st.column_config.NumberColumn("👍 좋아요", format="%d"),
                    "작성일": st.column_config.TextColumn("📅 작성일"),
                }
            )

        with tab3:
            s1, s2, s3, s4 = st.columns(4)
            top_comments = df[df["유형"] == "댓글"]
            reply_comments = df[df["유형"] == "↳ 답글"]
            s1.metric("전체 수집", f"{len(df)}개")
            s2.metric("댓글", f"{len(top_comments)}개")
            s3.metric("답글", f"{len(reply_comments)}개")
            s4.metric("좋아요 합계", f"{df['좋아요'].sum():,}")

            st.markdown("#### 🏆 좋아요 TOP 10 댓글")
            top10 = df.nlargest(10, "좋아요")[["작성자", "댓글", "좋아요", "작성일"]]
            st.dataframe(top10, use_container_width=True, hide_index=True)

        st.markdown("---")
        csv_data = df.to_csv(index=False, encoding="utf-8-sig")
        st.download_button(
            label="📥 CSV 파일 다운로드",
            data=csv_data,
            file_name=f"youtube_comments_{video_id}.csv",
            mime="text/csv",
            use_container_width=True
        )

    elif search_button and not url:
        st.warning("유튜브 URL을 입력해주세요!")


if __name__ == "__main__":
    main()
