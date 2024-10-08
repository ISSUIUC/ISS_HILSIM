import Card from 'react-bootstrap/Card';
import { Container } from 'react-bootstrap';
import { useState, useRef } from 'react';
import Button from 'react-bootstrap/Button';
import Collapse from 'react-bootstrap/Collapse';
import { useNavigate } from "react-router-dom"
import { KamajiJobTags } from './jobtags';

function JobItem(props) {
  const [open, setOpen] = useState(false);
  let borderColor = ''
  let has_start_time = false
  let has_end_time = true

  const navigate = useNavigate();

  if(!props.active) {
    return <></>;
  }

  
  let run_states = ["RUNNING", "SETUP_PRECOMPILE", "SETUP_COMPILING"]
  if(run_states.includes(props.job_data.run_status)){
    borderColor = "border-warning"
  } else if(props.job_data.run_status=="SUCCESS") {
    borderColor = "border-success"
  }

  if(props.job_data.run_start != null) {
    has_start_time = true
  }

  if(props.job_data.run_end != null) {
    has_end_time = true
  }

  return (
      <Card style={{textAlign: 'left', marginBottom: '10px'}}
            className={"border-3 rounded " + borderColor}
      >
        <Card.Body>
          <Card.Title className="cursor-pointer" onClick={() => {
            navigate(`/job?id=${props.job_data.run_id}`)
          }}>{props.job_data.run_id} : {props.job_data.user_id}</Card.Title>
          <Card.Text>
            <KamajiJobTags status={props.job_data.run_status}></KamajiJobTags>
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

export default JobItem;