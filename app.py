import streamlit as st
from groq import Groq

MODEL = "openai/gpt-oss-20b"

st.set_page_config(
    page_title="AI Content Assistant",
    page_icon="✍️",
    layout="centered",
)

st.title("✍️ AI Content Assistant")
st.write("Create ready-to-publish content with Groq AI.")


def generate_content(content_type, platform, topic, audience, tone):
    """Generate a post, caption, and hashtags with Groq."""
    try:
        api_key = st.secrets["GROQ_API_KEY"]
    except Exception:
        raise ValueError(
            "Groq API key is missing. Add GROQ_API_KEY to Streamlit Secrets."
        )

    prompt = f"""
You are a professional social media copywriter.

Create original, ready-to-publish content using these details:

Content Type: {content_type}
Platform: {platform}
Topic: {topic}
Target Audience: {audience}
Tone: {tone}

Return ONLY these three sections:

POST:
Write the complete main post.

CAPTION:
Write a suitable caption.

HASHTAGS:
Write 8-12 relevant hashtags.

Rules:
- Match the selected platform and audience.
- Match the requested tone.
- Stay focused on the topic.
- Make the content ready to publish.
- Do not explain your process.
- Do not add extra sections.
"""

    client = Groq(api_key=api_key)

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are an expert social media content writer.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
        max_tokens=1200,
    )

    return response.choices[0].message.content


def parse_result(result):
    """Separate the response into post, caption, and hashtags."""
    post = ""
    caption = ""
    hashtags = ""

    if "POST:" in result:
        text = result.split("POST:", 1)[1]
        if "CAPTION:" in text:
            post, text = text.split("CAPTION:", 1)
            if "HASHTAGS:" in text:
                caption, hashtags = text.split("HASHTAGS:", 1)
            else:
                caption = text
        else:
            post = text
    else:
        post = result

    return post.strip(), caption.strip(), hashtags.strip()


st.subheader("Create Your Content")

content_type = st.selectbox(
    "Content Type",
    [
        "Social Media Post",
        "Instagram Caption",
        "LinkedIn Post",
        "Facebook Post",
        "X/Twitter Post",
        "Promotional Post",
        "Educational Post",
    ],
)

platform = st.selectbox(
    "Platform",
    ["Instagram", "Facebook", "LinkedIn", "X/Twitter", "General Social Media"],
)

topic = st.text_area(
    "Topic",
    placeholder="Example: Benefits of learning English for career growth",
)

audience = st.text_input(
    "Target Audience",
    placeholder="Example: Pakistani university students",
)

tone = st.selectbox(
    "Tone",
    [
        "Professional",
        "Friendly",
        "Educational",
        "Persuasive",
        "Casual",
        "Inspirational",
        "Conversational",
        "Authoritative",
    ],
)

if st.button("✨ Generate Content", use_container_width=True):
    if not topic.strip():
        st.warning("Please enter a topic.")
        st.stop()

    if not audience.strip():
        st.warning("Please enter a target audience.")
        st.stop()

    with st.spinner("Generating your content..."):
        try:
            result = generate_content(
                content_type,
                platform,
                topic,
                audience,
                tone,
            )

            post, caption, hashtags = parse_result(result)

            st.success("Content generated successfully!")

            st.subheader("📝 Generated Post")
            st.write(post)

            st.divider()

            st.subheader("📌 Caption")
            st.write(caption)

            st.divider()

            st.subheader("#️⃣ Hashtags")
            st.write(hashtags)

        except ValueError as error:
            st.error(str(error))

        except Exception as error:
            message = str(error).lower()

            if "401" in message or "authentication" in message or "api key" in message:
                st.error("Your Groq API key is invalid or not configured.")
            elif "429" in message or "rate limit" in message:
                st.error("Groq rate limit reached. Please try again later.")
            elif "404" in message or "model" in message:
                st.error("The selected Groq model is unavailable. Check Groq's current model list.")
            elif "503" in message or "unavailable" in message:
                st.error("The AI service is temporarily unavailable. Please try again shortly.")
            else:
                st.error("Something went wrong. Please try again.")
