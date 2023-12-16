# views.py
from PyPDF2 import PdfReader
from django.http import HttpResponse, JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import UploadedFile, PDFContent,MessagesHistory
from .serializers import UploadedFileSerializer
import PyPDF2
import os
from django.shortcuts import get_object_or_404, render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import IsAuthenticated
from .serializers import MessageSerializer
from .models import MessagesHistory
import openai
from langchain.embeddings import OpenAIEmbeddings, SentenceTransformerEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain, RetrievalQA
from langchain.memory import ConversationBufferWindowMemory
from langchain.vectorstores import FAISS
from langchain.document_loaders import PyPDFLoader
import os
from dotenv import load_dotenv, find_dotenv
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.llms import OpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate



_ = load_dotenv(find_dotenv())
openai.api_key = os.getenv('OPENAI_API_KEY')

class FileUploadView(APIView):
    def post(self, request, *args, **kwargs):
        # Include 'session_id' in the request.data if sent from the frontend
        session_id = request.data.get('session_id', None)

        file_serializer = UploadedFileSerializer(data=request.data)

        if file_serializer.is_valid():
            # Pass 'session_id' when saving UploadedFile instance
            file_serializer.save(session_id=session_id)
            # Pass 'session_id' to associate with PDFContent instances
            content = self.parse_and_save_content(file_serializer.instance.file.path, session_id)
            # Fetch text chunks from the parsed and saved content
            text_chunks = self.get_text_chunks(content)
            # Generate embeddings and create a vector store
            vectorstore = self.vector_store(text_chunks)
            # Get or initialize the conversation chain from the session
            conversation_chain = self.get_conversation_chain(vectorstore)

            return Response(file_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def parse_and_save_content(self, file_path, session_id):
        content = """ """
        if file_path.endswith('.pdf'):
            with open(file_path, 'rb') as file:
                # pdf_reader = PyPDF2.PdfReader(file)
                # num_pages = len(pdf_reader.pages)

                # base_filename = os.path.splitext(os.path.basename(file_path))[0]
                text =""""""
                try:
                    pdf_reader = PdfReader(file)
                except (PdfReader.PdfReadError, PyPDF2.utils.PdfReadError) as e:
                    print(f"Failed to read {file}: {e}")

                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:  # checking if page_text is not None or empty string
                        text += page_text
                    else:
                        print(f"Failed to extract text from a page in {file}")


                title = os.path.splitext(os.path.basename(file_path))[0]
                pdf_content = PDFContent(title=title, content=text, session_id=session_id)
                pdf_content.save()
        else:
            pass

        return text

    def get_text_chunks(self, text):
        text_splitter = RecursiveCharacterTextSplitter(
            separators="\n",
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        chunks = text_splitter.split_text(text)
        return chunks

    def vector_store(self, text_chunks):
        persist_directory = 'chromadb'
        embedding = OpenAIEmbeddings(openai_api_key=os.getenv('OPENAI_API_KEY'))
        vectordb = Chroma.from_texts(texts=text_chunks,
                                         embedding=embedding,
                                         persist_directory=persist_directory)
        vectordb.persist()
        vectordb = None
        vectordb = Chroma(persist_directory=persist_directory,
                          embedding_function=embedding)
        return vectordb

    def get_conversation_chain(self, vectordb):
        memory = ConversationBufferWindowMemory(memory_key='chat_history', return_message=True)
        conversation_chain = ConversationalRetrievalChain.from_llm(
            llm=ChatOpenAI(model_name="gpt-3.5-turbo-16k", openai_api_key=os.getenv('OPENAI_API_KEY')),
            retriever=vectordb.as_retriever(),
            get_chat_history=lambda h: h,
            memory=memory
        )
        return conversation_chain



@method_decorator(csrf_exempt, name='dispatch')
class ChatBotView(APIView):

    def post(self, request):
        user_input = request.data.get('user_input')
        session_id = request.data.get('session_id')

        messages = []

        # Record user messages
        if user_input:
            try:
                user_message, created = MessagesHistory.objects.get_or_create(
                    session_id=session_id,
                    defaults={'text': []},
                )

                user_message.text.append({'sender': 'user', 'content': user_input})
                user_message.save()

                messages.extend(user_message.text)

                # Process user input and get bot response
                bot_response = self.process_user_query(user_input)
                bot_message = MessagesHistory.objects.get_or_create(
                    session_id=session_id,
                    content=bot_response,
                )

                bot_message.text.append({'sender': 'bot', 'content': bot_response})
                bot_message.save()
                messages.extend(bot_message.text)


            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'messages': messages}, status=status.HTTP_201_CREATED)

    def process_user_query(self, user_input, session_id):
        msg_history = MessagesHistory.objects.filter(session_id=session_id)

        msg_history_list = [{'role': message.sender, 'content': message.content} for message in msg_history]
        msg_history_list.append({'role': 'user', 'content': user_input})

        result = self.conversation_chain({"question": user_input, "chat_history": msg_history_list})
        msg_history_list.append({'role': 'assistant', 'content': result["answer"]})

        # MessagesHistory.objects.filter(session_id=session_id).delete()
        for message in msg_history_list:
            MessagesHistory.objects.create(sender=message['role'], content=message['content'], session_id=session_id)

        return result["answer"]










    # def initialize_chat_history(request):
    #     # Initialization logic
    #     request.session['doc_messages'] = [{"role": "assistant", "content": "Query your documents"}]
    #     request.session['chat_history'] = []
    #     return JsonResponse({"status": "success"})
    #
    # def process_user_query(request):
    #     if request.method == 'POST':
    #         user_input = request.POST.get('user_input')
    #
    #         # Ensure chat history is initialized
    #         if 'doc_messages' not in request.session:
    #             return JsonResponse({"status": "error", "message": "Chat history not initialized"})
    #
    #         # Add user's message to chat history
    #         request.session['doc_messages'].append({"role": "user", "content": user_input})
    #
    #         # Process the user's message using the conversation chain
    #         if 'conversation_chain' in request.session:
    #             result = request.session.conversation_chain({
    #                 "question": user_input,
    #                 "chat_history": request.session['chat_history']
    #             })
    #             bot_response = result["answer"]
    #
    #                 # Append the user's question and AI's answer to chat_history
    #             request.session['chat_history'].append({
    #                 "role": "user",
    #                 "content": user_input
    #             })
    #             request.session['chat_history'].append({
    #                 "role": "assistant",
    #                 "content": bot_response
    #             })
    #         else:
    #             bot_response = "Please upload a document first to initialize the conversation chain."
    #
    #         # Return the bot's response to the frontend
    #     return JsonResponse({"bot_message": bot_response, "status": "success"})
    #
    #     return JsonResponse({"status": "error", "message": "Invalid request method"})



    # def process_user_input(self, user_input, session_id):
    #     # Implement your logic to process user input and generate bot response
    #     # You can use NLP techniques, keyword matching, or other methods
    #
    #     # For example, let's assume the user is asking for information about a specific topic
    #     query_keywords = ['summary', 'information', 'details', 'about']
    #     if any(keyword in user_input.lower() for keyword in query_keywords):
    #         # Retrieve relevant information from the PDF content
    #         pdf_content = self.retrieve_pdf_content(session_id)
    #         # Implement your logic to extract relevant information based on the user's query
    #         # For demonstration purposes, let's assume you have a method to extract information
    #         # based on keywords
    #         extracted_info = self.extract_information_from_pdf(pdf_content, user_input)
    #         return extracted_info
    #
    #     # Add more conditions and logic based on your requirements
    #     return "I'm sorry, I couldn't understand your request."
    #
    # def retrieve_pdf_content(self, session_id):
    #     # Retrieve PDF content associated with the session_id
    #     try:
    #         pdf_content = PDFContent.objects.get(session_id=session_id)
    #         return pdf_content.content
    #     except PDFContent.DoesNotExist:
    #         return None
    #
    # def extract_information_from_pdf(self, pdf_content, user_input):
    #     # Implement your logic to extract relevant information from the PDF content
    #     # For demonstration purposes, let's assume a simple keyword-based extraction
    #     keywords = ['important', 'information', 'extracted']
    #     extracted_info = [word for word in pdf_content.split() if word.lower() in keywords]
    #     return ' '.join(extracted_info)







# Chatbot Messages View
# class ChatBotView(APIView):
#     def post(self, request, *args, **kwargs):
#         user_input = request.data.get('userInput', '')
#         dummy_message = request.data.get('dummymessage', '')
#
#         if user_input:
#             user_message = ChatHistory.objects.create(text=user_input, type='user')
#             if dummy_message:
#                 bot_message = ChatHistory.objects.create(text=dummy_message, type='bot')
#             return JsonResponse({'status': 'success'})
#         else:
#             return JsonResponse({'status': 'error', 'message': 'User input is empty.'})