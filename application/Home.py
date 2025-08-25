import streamlit as st

st.set_page_config(page_title="Smart Assistant", page_icon="💼", layout="wide")

# ==============================
# Session State for Navigation
# ==============================
if "page" not in st.session_state:
    st.session_state.page = "home"

def go_to(page_name):
    st.session_state.page = page_name
    st.rerun()

# ==============================
# Custom CSS for Fancy Buttons & Navbar Back Button
# ==============================
st.markdown("""
    <style>
        /* Generic Feature Buttons (Cards) */
        div.stButton > button:not(.back-home-btn) {
            background: linear-gradient(135deg, #00338D, #007BFF);
            color: white !important;
            font-size: 18px !important;
            font-weight: 600 !important;
            padding: 2rem !important;
            border-radius: 16px !important;
            border: none !important;
            box-shadow: 0px 4px 12px rgba(0,0,0,0.15);
            transition: all 0.3s ease-in-out;
            height: 180px !important;
            white-space: normal !important;
            text-align: center !important;
            line-height: 1.4em !important;
        }
        div.stButton > button:not(.back-home-btn):hover {
            transform: translateY(-6px) scale(1.03);
            box-shadow: 0px 10px 25px rgba(0,0,0,0.25);
            background: linear-gradient(135deg, #0055CC, #3399FF);
        }

        /* Fixed Back Button */
        .back-btn-container {
            position: fixed;
            top: 20px;
            left: 20px;
            z-index: 1000;
        }
        .back-btn-container button.back-home-btn {
            background: #f0f2f6 !important;
            color: #00338D !important;
            font-size: 14px !important;
            padding: 0.4rem 1rem !important;
            border-radius: 8px !important;
            border: 1px solid #d3d6db !important;
            box-shadow: none !important;
            height: auto !important;
            width: auto !important;
            min-width: unset !important;
            max-width: unset !important;
            transition: all 0.2s ease-in-out;
        }
        .back-btn-container button.back-home-btn:hover {
            background: #e4e8f0 !important;
            transform: none !important;
            box-shadow: 0px 2px 6px rgba(0,0,0,0.1);
        }
    </style>
""", unsafe_allow_html=True)

# ==============================
# BACK BUTTON (only show if not home)
# ==============================
if st.session_state.page != "home":
    st.markdown('<div class="back-btn-container">', unsafe_allow_html=True)
    if st.button("⬅️ Back to Home", key="back_home", help="Return to homepage"):
        go_to("home")
    st.markdown(
        """<script>
            const btn = window.parent.document.querySelector('button[kind=secondary]');
            if (btn) { btn.classList.add('back-home-btn'); }
        </script>""",
        unsafe_allow_html=True,
    )
    st.markdown('</div>', unsafe_allow_html=True)

# ==============================
# HOME PAGE
# ==============================
if st.session_state.page == "home":
    st.markdown('<h1 style="text-align:center;color:#00338D;">💼 Smart Assistant</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center;font-size:18px;color:#555;">AI-powered Document Q&A, Email Generation, and Support Automation</p>', unsafe_allow_html=True)

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        if st.button("📄\nDocument Q&A\nUpload and ask with RAG-based answers", key="docqa_btn", use_container_width=True):
            go_to("docqa")

    with col2:
        if st.button("✉️\nEmail Generator\nCreate professional emails instantly", key="email_btn", use_container_width=True):
            go_to("email")

    with col3:
        if st.button("💬\nSupport Chat\nGet answers or raise Jira tickets", key="chat_btn", use_container_width=True):
            go_to("chat")

    with col4:
        if st.button("⚙️\nSummarizer\nConfigure API keys & preferences", key="settings_btn", use_container_width=True):
            go_to("Summarizer")

    with col5:
        if st.button("⚙️\nNER\nNamed entity recognizer", key="nerbtn", use_container_width=True):
            go_to("NER")

# ==============================
# DOCUMENT Q&A PAGE
# ==============================
elif st.session_state.page == "docqa":
    st.header("📄 Document Q&A")
    import streamlit as st

    st.subheader("## 📄 Document Q&A – High-Level Architecture")

    st.graphviz_chart("""
    digraph {
        rankdir=LR;
        node [shape=box, style=rounded, fontsize=12, fontname="Helvetica"];

        Documents [label="📂 Company Documents\n(PDFs, Manuals, Guides)"];
        KnowledgeBase [label="📚 Knowledge Base\n(Vector Index)"];
        Embedder [label="🔎 Embedder\n(Understands Meaning of Text)"];
        Generator [label="💡 Generator\n(Writes Clear Answers)"];
        User [label="👩‍💼 End User\n(Employees / Customers)"];

        Documents -> Embedder [label="Convert to\nEmbeddings"];
        Embedder -> KnowledgeBase [label="Store & Organize"];
        User -> Embedder [label="Ask Question\n(Convert to Embedding)"];
        KnowledgeBase -> Generator [label="Relevant Context"];
        Embedder -> KnowledgeBase [style=dashed, color=gray];
        Generator -> User [label="Answer with Context"];
    }
    """)

    st.markdown("""
    ### 🟢 How It Works (Simple Steps)
    1. **Upload & Organize Documents**  
       - All company knowledge (PDFs, manuals, guides) is stored in one place.  

    2. **Build a Knowledge Base**  
       - The system organizes the content so it can be searched quickly.  

    3. **Ask Questions in Plain English**  
       - Users type natural questions without needing to know where the document is.  

    4. **Get Instant, Accurate Answers**  
       - The system searches documents and provides a clear, trusted answer.  

    ---

    ✅ **Outcome for Business:** Faster decisions, less manual searching, and consistent knowledge across the organization.
    """)

    st.markdown("""
    ### 📄 Advantages of Document Q&A with RAG  

    1. **Faster Access to Information**  
       - Employees can ask questions in plain English and get instant answers.  
       - No need to search through multiple files or manuals.  

    2. **Improved Accuracy**  
       - The system looks at company documents before responding.  
       - Reduces the chances of wrong or misleading answers.  

    3. **Time Savings**  
       - Cuts down hours spent searching documents.  
       - Frees up employees to focus on higher-value tasks.   

    4. **Scales with Knowledge**  
       - Works with thousands of documents.  
       - Can easily grow as more documents are added.  


    ---

    ⚡ **In short:**  
    This solution helps teams **find the right information quickly, accurately, and at scale**, leading to **better decisions and higher productivity**.  
    """)

    st.header("In-Product Use cases ")
    st.markdown("""
        **Tax credits**, R&D contract document processing
        
        **Confluence Helper**, A confluence helper which would help product , business and development teams to increase productivity
        """)


# ==============================
# EMAIL PAGE
# ==============================
elif st.session_state.page == "email":
    st.header("✉️ Email Generator")
    st.header("Architecture")
    st.graphviz_chart("""
    digraph {
        rankdir=LR;
        UserInput [label="🧑 User Input"];
        PrePrompt [label="📝 Build Prompt"];
        Model [label="🤖 Text2Text Model "];
        Email [label="📨 Generated Email"];
        UI [label="📊 Streamlit UI"];

        UserInput -> PrePrompt -> Model -> Email -> UI;
    }
    """)

    st.markdown("""
    ### ✉️ Advantages of AI-Based Email Generation  

    1. **Time Efficiency**  
       - Drafts emails in seconds, saving effort on repetitive or formal communication.  
       - Frees up time to focus on higher-priority tasks.  

    2. **Consistency & Professionalism**  
       - Ensures tone, structure, and formatting remain polished across all messages.  
       - Reduces chances of grammatical or stylistic errors.  

    3. **Personalization at Scale**  
       - Can adapt content for different recipients while maintaining a personalized touch.  
       - Useful for customer support, marketing, or client communication.  

    4. **Creativity Boost**  
       - Provides suggestions for phrasing, subject lines, and tone variations (formal, friendly, persuasive, etc.).  
       - Helps overcome writer’s block.  

    5. **Multi-Language Support**  
       - Many AI models can translate or generate emails in multiple languages.  
       - Ideal for global teams and cross-border communication.  

    6. **Integration with Workflows**  
       - Can connect with CRMs, ticketing systems, or support chatbots.  
       - Automates follow-ups, reminders, and reporting.  

    7. **Error Reduction**  
       - Minimizes typos, missing details, and inconsistent wording.  
       - Helps maintain professionalism in client communications.  

    ---

    ⚡ **In short:** AI-powered email generation makes communication **faster, smarter, and more reliable**, while still leaving room for human oversight where needed.
    """)

    st.header("In-Product Use cases ")
    st.markdown("""
    In Tax credits and other products,We have the capability to send custom emails , We can leverage AI to help operations team to phrase the emails faster, accurate and have better tone.  
    We could also minimize the potential human errors. 
    """)

# ==============================
# CHAT PAGE
# ==============================
elif st.session_state.page == "chat":
    st.header("💬 Support Chat")
    import streamlit as st

    st.markdown("## 💬 Support Chatbot – High-Level Architecture")

    st.graphviz_chart("""
    digraph {
        rankdir=LR;
        node [shape=box, style=rounded, fontsize=12, fontname="Helvetica"];

        User [label="👩‍💻 User Query\n(Customer Question)"];
        Preprocess [label="🧹 Preprocessing\n(Clean & Standardize)"];
        Embedder [label="🔎 Embedder\n(Understands Meaning)"];
        Retriever [label="📚 Knowledge Base\n(Retrieves Relevant Info)"];
        Generator [label="🤖 Response Generator\n(Creates Helpful Answer)"];
        Answer [label="📝 Response\n(Accurate & Friendly)"];
        Business [label="🏢 Business\n(Reduced Support Load, Faster Resolutions)"];

        User -> Preprocess -> Embedder -> Retriever -> Generator -> Answer -> Business;
    }
    """)

    st.markdown("""
    ### 🟢 How It Works (Support Chatbot Flow)

    1. **User Query**  
       - Customers ask questions (e.g., "How do I reset my password?").  

    2. **Preprocessing**  
       - The system cleans and formats the query.  

    3. **Embedder**  
       - AI understands the **intent and meaning** behind the question.  

    4. **Knowledge Base Search (Retriever)**  
       - Looks up the most **relevant answers** from company FAQs, documents, or prior tickets.  

    5. **Response Generator**  
       - AI creates a **clear, accurate, and user-friendly response**.  

    6. **Final Response**  
       - Delivered back to the customer instantly.  

    7. **Business Value**  
       - Leadership sees **faster support resolutions**, **lower manual effort**, and **improved customer satisfaction**.  

    ---

    ✅ **Outcome for Business:**  
    - **24/7 availability**: Customers get instant support anytime.  
    - **Reduced costs**: Automates repetitive queries so agents handle only complex issues.  
    - **Consistency**: Provides **standardized and reliable answers**.  
    - **Scalability**: Can handle **thousands of users simultaneously** without adding staff.  
    - **Better Insights**: Tracks common queries to **improve products and services**.  
    """)


# ==============================
# SETTINGS PAGE
# ==============================
elif st.session_state.page == "Summarizer":
    st.header("⚙️ Summarizer")
    import streamlit as st

    st.markdown("## ✨ Summarizer – High-Level Architecture")

    st.graphviz_chart("""
    digraph {
        rankdir=LR;
        node [shape=box, style=rounded, fontsize=12, fontname="Helvetica"];

        Text [label="📄 Input Text\n(Emails, Reports, Documents)"];
        Preprocess [label="🧹 Preprocessing\n(Clean & Prepare Data)"];
        Embedder [label="🔎 Embedder\n(Understands Context)"];
        Generator [label="🤖 Summarizer Model\n(Creates Short Version)"];
        Summary [label="📝 Summary Output\n(Key Points, Insights)"];
        User [label="👩‍💼 Business User\n(Fast Understanding, Decisions)"];

        Text -> Preprocess -> Embedder -> Generator -> Summary -> User;
    }
    """)

    st.markdown("""
    ### 🟢 How It Works (Summarizer Flow)

    1. **Provide Input Text**  
       - Long reports, customer feedback, meeting notes, or research documents.  

    2. **Preprocessing**  
       - Text is cleaned and standardized to remove noise.  

    3. **Embedder**  
       - The system **understands context and meaning** from the text.  

    4. **Summarizer Model**  
       - AI creates a **concise summary** that captures the key points while ignoring unnecessary details.  

    5. **Summary Output**  
       - The output is a **clear, easy-to-read summary**.  

    6. **Business User Benefits**  
       - Users get the **essence of the document quickly**, without reading the whole thing.  

    ---

    ✅ **Outcome for Business:**  
    - Saves **time** by turning long content into short, actionable insights.  
    - Helps **leadership** stay informed without reading full reports.  
    - Improves **decision-making** with quick access to key facts.  
    - Increases **productivity** for teams dealing with large volumes of text.  
    """)

    st.header("In-Product Use cases ")
    st.markdown("""
            Calls between client and Operations can be summarized to get faster understanding of the moments of the meeting""")

elif st.session_state.page == "NER":
    st.header("⚙️ Named entity recognizer")
    st.markdown("## 🏷️ Named Entity Recognition (NER) – High-Level Architecture")

    st.graphviz_chart("""
    digraph {
        rankdir=LR;
        node [shape=box, style=rounded, fontsize=12, fontname="Helvetica"];

        Text [label="📄 Input Text\n(Emails, Reports, Chats)"];
        Preprocess [label="🧹 Preprocessing\n(Clean & Prepare Data)"];
        NERModel [label="🤖 NER Model\n(Understands Language)"];
        Entities [label="🏷️ Extracted Entities\n(Names, Dates, Places, IDs)"];
        User [label="👩‍💼 Business User\n(Search, Analytics, Automation)"];

        Text -> Preprocess -> NERModel -> Entities -> User;
    }
    """)

    st.markdown("""
    ### 🟢 How It Works (NER Flow)

    1. **Provide Input Text**  
       - Emails, reports, customer chats, or policies are fed into the system.  

    2. **Preprocessing**  
       - Text is cleaned and prepared (remove noise, standardize formats).  

    3. **NER Model**  
       - AI scans the text and **detects important entities** such as:  
         - 👤 **People** (e.g., customer names, employee names)  
         - 🏢 **Organizations** (e.g., company names, departments)  
         - 📍 **Locations** (e.g., cities, branches, addresses)  
         - 📅 **Dates & Times** (e.g., deadlines, meeting dates)  
         - 🔑 **IDs / Codes** (e.g., invoice numbers, policy IDs)  

    4. **Entity Extraction**  
       - The model tags these entities so they can be **searched, tracked, or analyzed** easily.  

    5. **Business User Benefits**  
       - Users don’t need to **read everything manually** — they can quickly find **who, what, where, and when**.  

    ---

    ✅ **Outcome for Business:**  
    - Speeds up **document review** (legal, compliance, HR).  
    - Enables **better analytics** (e.g., track customer names, identify key partners).  
    - Automates **manual data entry & categorization**.  
    - Reduces errors and saves time.  
    
    
    """)

    st.header("In-Product Use cases ")
    st.markdown("""
        In Tax credits and other products, While we process Payroll Tax Credit and R&d tax credit , 
        we will have the need to read data from 6765 and also other client documents. We can use NER to analyze and extract the information from the docs.
        This would save us a lot of time, Would also minimize the change of errors. 
        """)
