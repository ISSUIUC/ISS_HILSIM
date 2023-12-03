import Card from 'react-bootstrap/Card';
import { Container } from 'react-bootstrap';
import { useState, useRef } from 'react';
import Button from 'react-bootstrap/Button';
import Collapse from 'react-bootstrap/Collapse';

function QueueItem(props) {
  const [open, setOpen] = useState(false);
  let borderColor = ''
  
  if(props.status=="RUNNING"){
    borderColor = "border-warning"
  }

  if(props.status=="SUCCESS"){
    return <div key={props.id}></div>
  }
  return (
      <Card style={{textAlign: 'left', marginBottom: '10px'}}
            className={"border-3 rounded " + borderColor}
      >
        <Card.Body>
          <Card.Title>{props.username}</Card.Title>
          <Card.Text>
            {props.id}
          </Card.Text>
          <Card.Text>
            Branch: {props.branch}
          </Card.Text>
          <Button
            onClick={() => setOpen(!open)}
            aria-controls="example-collapse-text"
            aria-expanded={open}
            className="p-0 bg-white border-0 text-justify text-left"
          >
            <p className='text-primary text-decoration-underline text-left'>More</p>
          </Button>
          <Collapse in={open}>
            <Card.Text>
              Submit time {props.submit_time}
            </Card.Text>
          </Collapse>
        </Card.Body>
      </Card>
  );
}

export default QueueItem;