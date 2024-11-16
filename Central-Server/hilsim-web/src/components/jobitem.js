import Card from 'react-bootstrap/Card';
import { Container, Form } from 'react-bootstrap';
import { useState, useRef } from 'react';
import Button from 'react-bootstrap/Button';
import Collapse from 'react-bootstrap/Collapse';
import Modal from 'react-bootstrap/Modal';
import { useNavigate } from "react-router-dom"
import { KamajiJobTags } from './jobtags';
import { api_url } from '../dev_config';

function JobItem(props) {
  const [open, setOpen] = useState(false);
  const [showEditScreen, setShowEditScreen] = useState(false);
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

  const show_edit_screen = () => {
    setShowEditScreen(true);
  }

  const close_edit_screen = () => {
    setShowEditScreen(false);
  }

  const edit_job = () => {
    fetch(api_url + '/api/job/update', {
      method: 'POST',
      headers: { 
        "Content-Type": "application/json",
        "ngrok-skip-browser-warning": "true",
        "Access-Control-Allow-Origin": "*"
      },
      body: JSON.stringify({
        new_commit: document.getElementById('formHash').value,
        new_branch: document.getElementById('formBranch').value,
        run_id: props.job_data.run_id
      })
    })
    .then(response => response.json())
    .then(json_data => {
      console.log(json_data);
      setShowEditScreen(false);
    })
    .catch(error => {
      console.error('Error:', error);
    });
  }


  return (
      <Card style={{textAlign: 'left', marginBottom: '10px'}}
            className={"border-3 rounded " + borderColor}
      >
        <Card.Body>
          <div style={{flexDirection: 'row', justifyContent: 'space-between'}}>
            <Card.Title className="cursor-pointer" onClick={() => {
              navigate(`/job?id=${props.job_data.run_id}`)
            }}>{props.job_data.run_id} : {props.job_data.user_id}
            </Card.Title>
            <Button variant="danger" onClick={show_edit_screen}>Edit</Button>
          </div>
          
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
        <Modal show={showEditScreen} onHide={close_edit_screen}>
        <Modal.Header closeButton>
          <Modal.Title>Edit Job</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form>
            <Form.Group controlId="formHash">
              <Form.Label>Hash</Form.Label>
              <Form.Control type="text" placeholder="Enter new Hash" defaultValue={props.job_data.git_hash} />
            </Form.Group>
            <Form.Group controlId="formBranch">
              <Form.Label>Branch</Form.Label>
              <Form.Control type="text" placeholder="Enter new Branch" defaultValue={props.job_data.branch} />
            </Form.Group>
            {/* Add more input elements as needed */}
          </Form>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={close_edit_screen}>
            Close
          </Button>
          <Button variant="primary" onClick={edit_job}>
            Save Changes
          </Button>
        </Modal.Footer>
      </Modal>
      </Card>
  );
}

export default JobItem;