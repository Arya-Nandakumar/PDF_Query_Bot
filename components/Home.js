import React, { Component } from 'react';
import { InputText } from 'primereact/inputtext'; 
import { Button } from 'primereact/button'; 
import './home.css';
import Navbar from './Navbar';

class Home extends Component {

  render() {
    return (
      <div className="homie">
        <Navbar/>
      </div>
    );
  }
}

export default Home;
