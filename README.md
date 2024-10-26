## Archive Flow: Intelligent Retrieval-Augmented Generation Assistant

<img src="./Miscellaneous/imgs/Demo1.png">

---

## SECTION 2 : EXECUTIVE SUMMARY / PAPER ABSTRACT
In an increasingly data-driven world, efficient and accessible information management is paramount for both businesses and individuals. ArchiveFlow, as a Retrieval-Augmented Generation (RAG) system, addresses this need by enhancing archiving processes through advanced document management and retrieval capabilities. This system combines retrieval and generation technologies to streamline the storage, classification, and retrieval of documents, aiming to reduce the time spent searching for information and improve overall productivity.

Our team designed ArchiveFlow with a modular architecture, incorporating both a front-end user interface and a robust back-end, developed using the Sanic framework, and supported by a Milvus vector database and MySQL for data management. The backend autonomously processes uploaded files by categorizing and indexing them using machine learning and pre-configured rules. By embedding documents with the BCE-embedding-base_v1(NetEase Open Source) model into a 768-dimensional vector space, ArchiveFlow enables rapid and accurate retrieval of relevant documents using Milvus, followed by reranking and context expansion to ensure comprehensive results. This two-stage search process optimizes the system’s speed and accuracy, significantly enhancing user experience.

To support high data loads, ArchiveFlow includes robust load balancing, user management, and permissions settings that ensure data security and scalability. Each user can create and manage personalized knowledge repositories, tailored to their specific information needs, allowing more efficient document organization and retrieval.

As ArchiveFlow evolves, future improvements may include more intelligent AI-driven classification, expanded cloud service integration, and customizable system configurations. We invite stakeholders to explore the potential of ArchiveFlow to meet their document management and retrieval needs, whether in small-scale personal applications or larger corporate environments.

---

## SECTION 3 : CREDITS / PROJECT CONTRIBUTION

| Official Full Name  | Student ID (MTech Applicable)  | Work Items (Who Did What) | Email (Optional) |
| :------------ |:---------------:| :-----| :-----|
| Wang Wenjie | A0296855H | **(Full Stack)**<br/>**Back-end**: Development of service layer and relevant SDKs such as the file parsing module, model manager module and etc; system architecture design;<br/>**Front-end**: Interface enhancement and optimization;<br/>**Server Operations**: Deployment of the entire system on the server, database design and management;<br/>**Other work**:System Architecture Description Video,  Optimization the final team report and | E1350993@u.nus.edu |
| Wu Zhengxi | A0296199E | **Back-end**: Development of Relevant APIs, such as file management, LLMs chat and etc; The workflow from file content parsing to vector embedding and storage in the database<br />**Front-end**: Interface Optimization;<br />**Other work**: Video of System Promotion | e1350337@u.nus.edu |
| Sun Yanshu | A0296705U | **Front-end**:Website design including Login, chat interface and File management pages, completing relevant js scripts these pages used,  Interface enhancement and optimization.<br />**Back-end:**Development of  the URL scraping in file parsing module.<br />**Other work**: Preparation of  final team report and user guide; mapped system functionalities against knowledge | e1350843@u.nus.edu |

---

## SECTION 4 : VIDEO OF SYSTEM MODELLING & USE CASE DEMO

[![Sudoku AI Solver](http://img.youtube.com/vi/-AiYLUjP6o8/0.jpg)](https://youtu.be/-AiYLUjP6o8 "Sudoku AI Solver")

Note: It is not mandatory for every project member to appear in video presentation; Presentation by one project member is acceptable. 
More reference video presentations [here](https://telescopeuser.wordpress.com/2018/03/31/master-of-technology-solution-know-how-video-index-2/ "video presentations")

---

## SECTION 5 : USER GUIDE

`Refer to appendix <Installation & User Guide> in project report at Github Folder: ProjectReport`

### [ 1 ] To run the system using iss-vm

> download pre-built virtual machine from http://bit.ly/iss-vm

> start iss-vm

> open terminal in iss-vm

> $ git clone https://github.com/telescopeuser/Workshop-Project-Submission-Template.git

> $ source activate iss-env-py2

> (iss-env-py2) $ cd Workshop-Project-Submission-Template/SystemCode/clips

> (iss-env-py2) $ python app.py

> **Go to URL using web browser** http://0.0.0.0:5000 or http://127.0.0.1:5000

### [ 2 ] To run the system in other/local machine:
### Install additional necessary libraries. This application works in python 2 only.

> $ sudo apt-get install python-clips clips build-essential libssl-dev libffi-dev python-dev python-pip

> $ pip install pyclips flask flask-socketio eventlet simplejson pandas

---
## SECTION 6 : PROJECT REPORT / PAPER

`Refer to project report at Github Folder: ProjectReport`

**Recommended Sections for Project Report / Paper:**
- Executive Summary / Paper Abstract
- Sponsor Company Introduction (if applicable)
- Business Problem Background
- Market Research
- Project Objectives & Success Measurements
- Project Solution (To detail domain modelling & system design.)
- Project Implementation (To detail system development & testing approach.)
- Project Performance & Validation (To prove project objectives are met.)
- Project Conclusions: Findings & Recommendation
- Appendix of report: Project Proposal
- Appendix of report: Mapped System Functionalities against knowledge, techniques and skills of modular courses: MR, RS, CGS
- Appendix of report: Installation and User Guide
- Appendix of report: 1-2 pages individual project report per project member, including: Individual reflection of project journey: (1) personal contribution to group project (2) what learnt is most useful for you (3) how you can apply the knowledge and skills in other situations or your workplaces
- Appendix of report: List of Abbreviations (if applicable)
- Appendix of report: References (if applicable)

---
## SECTION 7 : MISCELLANEOUS

`Refer to Github Folder: Miscellaneous`

### HDB_BTO_SURVEY.xlsx
* Results of survey
* Insights derived, which were subsequently used in our system
