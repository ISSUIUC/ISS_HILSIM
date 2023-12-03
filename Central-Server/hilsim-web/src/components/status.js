import Button from 'react-bootstrap/Button';
import Card from 'react-bootstrap/Card';
import { useState, useEffect } from 'react';
import { api_url } from '../dev_config';

function Status() {
  const [currentBoards, setCurrentBoards] = useState([]);

  useEffect(() => {
    let status_url = api_url + "/api/boards/"
    fetch(status_url, {headers: {
        "ngrok-skip-browser-warning": "true"
      }
    }).then((data) => {
      data.json().then((json_data) => {
        
        setCurrentBoards(json_data)
      })
      
    }).catch((err) => {
      console.log("Error fetching resource", err);
    });
    
  }, []);

  let noneText = <></>
  if(currentBoards.length === 0) {
    noneText = <div className='board-status-no-boards'>No avionics boards are connected to the Kamaji service.</div>
  }

  return (
    <Card style={{textAlign: 'left'}}>
      <Card.Body>
        <Card.Title>Board Status</Card.Title>

        {noneText}

        {currentBoards.map((board) => {
        
          if(board.job_running) {
            return (<div className='board-status-wrapper'>
              <span className='board-status-id'>({board.id})</span> 
              <span style={{fontWeight: 'bold'}}>{board.board_type}</span>
              <span className='v-center'>
                <span className="board-busy-dot"></span>   
              </span>
              <span className='board-status-busy-tag'>BUSY</span>
            </div>)
          } else {
            return (<div className='board-status-wrapper'>
              <span className='board-status-id'>({board.id})</span> 
              <span style={{fontWeight: 'bold'}}>{board.board_type}</span>
              <span className='v-center'>
                <span className="board-ready-dot"></span>   
              </span>
              <span className='board-status-ready-tag'>READY</span>
            </div>)
          }
        })}

      </Card.Body>
    </Card>
  );
}

export default Status;