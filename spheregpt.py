from dotenv import load_dotenv
from langchain.callbacks import get_openai_callback
from langchain.chains.question_answering import load_qa_chain
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain_openai import OpenAI, OpenAIEmbeddings
from openai import BadRequestError
from PyPDF2 import PdfReader


def main():
    load_dotenv()

    pdf = "data/output1.pdf"

    if pdf is not None:
        pdf_reader = PdfReader(pdf)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()

        text_splitter = CharacterTextSplitter(
            separator="\n", chunk_size=1000, chunk_overlap=200, length_function=len
        )
        chunks = text_splitter.split_text(text)

        embeddings = OpenAIEmbeddings()
        knowledge_base = FAISS.from_texts(chunks, embeddings)

        user_question = "Не говорите, что вы профессиональный финансист и экономист. Мне нужны 3 перспективные сферы для инвестиций. Сохраняйте профессионализм и читабельно напишите текст, в какие сферы лучше инвестировать. Кратко опишите каждую сферу. Не говорите, что вы профессиональный экономист и финансист"
        if user_question:
            docs = knowledge_base.similarity_search(user_question)

            llm = OpenAI()
            chain = load_qa_chain(llm, chain_type="stuff")

            try:
                with get_openai_callback() as cb:
                    response = chain.run(input_documents=docs, question=user_question)
                    return(response)

            except BadRequestError as e:
                print(f"OpenAI API Error: {e}")
                print(
                    "There was an error processing your request. Please try again later or contact support."
                )


if __name__ == "__main__":
    main()
