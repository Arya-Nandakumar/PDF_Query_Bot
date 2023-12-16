import React, { Component } from 'react';
import './faq.css';
import { v4 as uuidv4 } from 'uuid';
import { InputText } from 'primereact/inputtext';
import { Button } from 'primereact/button';
import MdOutlineUploadFile from '@mui/icons-material/UploadFile';
import backgroundImg from '../assets/header_background.png';
import { NavLink } from 'react-router-dom';

class FAQBot extends Component {
  state = {
    file: null,
    fileName: '',
    uploading: false,
    uploadError: null,
    text: '',
    messages: [],
    userInput: '',
    // dummymessage: 'Howdy There! FAQBot At Your Service!', // Initial dummy message
    session_id: '',
    showChatBox: false, 
  };

  componentDidMount() {
    const session_id = uuidv4();
    this.setState({ session_id });
  }

  handleFileUpload = (e) => {
    const file = e.target.files[0];
    const fileName = file ? file.name : '';
    this.setState({ file, fileName, uploadError: null, });
  };

  handleUpload = async () => {
    const { file, session_id } = this.state;
    if (!file) {
      return;
    }
    this.setState({ uploading: true, uploadError: null });
    
    try {
      const formData = new FormData();
      formData.append('file', file, file.name);
      formData.append('session_id', session_id);
      
      const response = await fetch('http://localhost:8000/faqbot/upload/', {
        method: 'POST',
        body: formData,
      });
  
      if (response.ok) {
        // After successful upload, call the parse_and_save_content endpoint
        await fetch(`http://localhost:8000/faqbot/parse-and-save/${file.name}/`);
        
        this.setState({ uploading: false, fileName: file.name, text: 'File uploaded successfully!' });
        setTimeout(() => {
          this.setState({ text: '', fileName: '' });
          this.setState({ showChatBox: true });

        }, 3000);
      } else {
        const errorData = await response.json();
        this.setState({ uploading: false, uploadError: errorData.message });
      }
    } catch (error) {
      console.error('Error uploading file:', error);
      this.setState({ uploading: false, uploadError: 'An error occurred during upload.' });
    }
  };
  
  


  handleTextChange = (e) => {
    const text = e.target.value;
    this.setState({ text });
  };


  handleUserInput = (e) => {
    this.setState({ userInput: e.target.value });
  };

  handleSendMessage = () => {
    const { userInput, session_id } = this.state;
  
    if (userInput) {
      const newMessage = { text: userInput, type: 'user' };
  
      this.setState((prevState) => ({
        messages: [...prevState.messages, newMessage],
        userInput: '',
      }));
  
      fetch('http://localhost:8000/faqbot/handle_message/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ user_input: userInput, session_id: session_id }),
      })
        .then(response => {
          if (!response.ok) {
            throw new Error('Network response was not ok');
          }
          return response.json();
        })
        .then(data => {
          const botResponse = { text: data.bot_message, type: 'bot' };
  
          this.setState((prevState) => ({
            messages: [...prevState.messages, botResponse],
          }));
        })
        .catch(error => {
          console.error('Error:', error);
        });
    }
  };
  
  
  
  

  render() {

    const {
      fileName,
      uploading,
      uploadError,
      text,
      messages,
      userInput,
      showChatBox,
    } = this.state;
    const sWidth = window.screen.width;
    
    return (
      <div className="faqbot-container">
        <img className='hbackground' src={backgroundImg} alt="background" />
        
        <div className='items'>
          <span>
            &nbsp;
            <b>
            <NavLink to="/" style={{ textDecoration: 'none', color: 'inherit' }}> <span  style={{ cursor: "pointer" }} className="hoverableLink"> Home </span>&ensp;&ensp;&ensp;&ensp;&ensp;</NavLink>
              <span style={{ cursor: "pointer" }} className="hoverableLink"> What is FAQBot ? </span>&ensp;&ensp;&ensp;&ensp;&ensp;
              <span style={{ cursor: "pointer" }} className="hoverableLink"> Key Features &nbsp;</span>
            </b>
          </span>
        </div>

        <div className='bodyContent' style={{ left: sWidth / 2 - (sWidth / 5) }}>
        <span className='title' style={{cursor: "pointer"}} >FAQ BOT 📑</span><br />
          <br />
        </div>



        <div className="container">
        <div className="fileupload">
          <h2>Upload Documents</h2>
          <label>
            <MdOutlineUploadFile fontSize="large" />
            <p>Upload a PDF File</p>
            <input type="file" accept="application/pdf" onChange={this.handleFileUpload} />
          </label>
          {fileName && !text && (
            <>
              <p>File to be Uploaded : {fileName}</p>
              <button type="button" onClick={this.handleUpload} disabled={uploading}>
                {uploading ? 'Uploading...' : 'Upload'}
              </button>
              {uploadError && <p style={{ color: 'red' }}>{uploadError}</p>}
            </>
          )}
          {text && <p>{text}</p>}
        </div>
      </div>


      {showChatBox && (
          <div className="chat-container">
            <div className="chat-messages">
              {messages.map((message, index) => (
                <div
                  key={index}
                  className={`message ${message.type === 'user' ? 'user-message' : 'bot-message'}`}
                >
                  {message.text}
                </div>
              ))}
            </div>
            <div className="chat-box">
              <h3>Query the document!</h3>
              <div className="chat-input">
                <InputText
                  className='textarea'
                  value={userInput}
                  onChange={this.handleUserInput}
                  placeholder="Chat with me :)"
                />
                <Button
                  className='send'
                  icon="pi pi-send"
                  onClick={this.handleSendMessage}
                />
              </div>
            </div>
          </div>
        )}




        {/* footer */}
        <div>
            <img className='fbackground' src={backgroundImg} alt="background" />
            <div className='footerContent'>
                <br />
                <br />
                <br />
                <br />
                <br />
            </div>
        </div>


      </div>
    );
  }
}

export default FAQBot;
