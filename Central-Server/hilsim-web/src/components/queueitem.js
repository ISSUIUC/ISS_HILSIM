import Card from 'react-bootstrap/Card';
import { Container } from 'react-bootstrap';
import { useState, useRef } from 'react';
import Button from 'react-bootstrap/Button';
import Collapse from 'react-bootstrap/Collapse';

function QueueItem(props) {
  const [open, setOpen] = useState(false);
  let borderColor = ''
  let showStartTime = 'hidden'

  
  if(props.job_data.status=="RUNNING"){
    borderColor = "border-warning"
  } else if(props.job_data.status=="SUCCESS") {
    borderColor = "border-success"
  }

  if(props.job_data.date_start!==null) {
    showStartTime = ''
  }

  if(props.job_data.status=="SUCCESS"){
    return <div key={props.job_data.id}></div>
  }
  return (
      <Card style={{textAlign: 'left', marginBottom: '10px'}}
            className={"border-3 rounded " + borderColor}
      >
        <Card.Body>
          <Card.Title>{props.job_data.user_id}</Card.Title>
          <Card.Text>
            {props.job_data.run_id}
          </Card.Text>
          <Card.Text>
            Branch: {props.job_data.branch}
          </Card.Text>
          <hr/>
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
              Submit time: {props.job_data.submitted_time}
            </Card.Text>
          </Collapse>
        </Card.Body>
      </Card>
  );
}

export default QueueItem;