import React, { Component } from 'react';
import { Link } from 'react-router-dom';
import './navbar.css';

class Navbar extends Component {
    render() {
        return (
            <div>
                <nav className="navbar">
                    <div className="navbar-title">
                    </div>
                    <div className="navbar-links-column"> 
                        <Link to="home" className='home-link'>Home</Link> 
                        <Link to="faq-bot" className='faq-link'>FAQ Bot</Link> 
                        <Link to="contact" className='contact-link'>Contact</Link> 
                    </div>
                </nav>
            </div>
        )
    }
}

export default Navbar;
