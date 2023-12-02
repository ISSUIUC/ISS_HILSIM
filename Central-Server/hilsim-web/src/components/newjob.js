import Button from 'react-bootstrap/Button';
import Card from 'react-bootstrap/Card';
import Row from 'react-bootstrap/esm/Row';
import Col from 'react-bootstrap/esm/Col';
import { Form } from 'react-bootstrap';
import { useState, useEffect } from 'react';
import { api_url } from '../dev_config';
import { useNavigate } from "react-router-dom"
import Spinner from 'react-bootstrap/Spinner';

function NewJob() {
  const [avionics, setAvionics] = useState("none");
  const [avionicsRepo, setAvionicsRepo] = useState("")
  const [branches, setBranches] = useState([]);
  const [selectedBranch, setSelectedBranch] = useState("none")
  const [defaultBranch, setDefaultBranch] = useState("none")
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const navigate = useNavigate()

  useEffect(() => {
    if(avionics == "none") {
      return;
    }
    let branch_url = `https://api.github.com/repos/ISSUIUC/${avionicsRepo}/branches`
    fetch(branch_url).then((data) => {
      data.json().then((json_data) => {
        setBranches(json_data)
      })
    })
  }, [avionics])

  let branchSelect = (<Form.Select aria-label="Branch-Select" disabled>
      <option>Select an avionics system first</option>
    </Form.Select>);

  if(avionics != "none") {
    branchSelect = (<Form.Select aria-label="Branch-Select" onChange={(event) => {
      setSelectedBranch(event.target.value)
    }}>
    <option value="none">Select a branch for {avionics}</option>
    <option key={defaultBranch} value={defaultBranch}>{defaultBranch}</option>
    {branches.map((branch) => {
      return <option key={branch.name} value={branch.name}>{branch.name}</option>
    })}
  </Form.Select>);
  }

  function submitJob() {
    console.log(avionics, selectedBranch)
    setSubmitting(true)
    fetch(api_url + `/api/jobs/queue?commit=0000&username=test_usear&branch=${selectedBranch}`, {headers: {
      "ngrok-skip-browser-warning": "true"
    }}).then((data) => {
      data.json((json_data) => {
        // at one point we'll redirect to a job page, so we want to keep this here
        // TODO: add redirects to job page
      })
      navigate("/")
    }).catch((err) => {
      setError(err.message);
      setSubmitting(false)
    })
  }

  return (
    <Card style={{textAlign: 'left', marginTop: '20px'}}>
      <Card.Header style={{fontWeight: 'wbold', textAlign: 'left'}}>Submit Job</Card.Header>
      <Card.Body>
      <Form>
      <Form.Group as={Row} className="mb-3" controlId="formHorizontalEmail">
        <Form.Label column sm={2}>
          Email/User
        </Form.Label>
        <Col sm={10}>
          <Form.Control disabled readonly type="email" placeholder=" * This field will be automatically filled in *" />
        </Col>
      </Form.Group>

      <Form.Group as={Row} className="mb-3" controlId="jobDescription">
        <Form.Label column sm={2}>
          Description
        </Form.Label>
        <Col sm={10}>
          <Form.Control as="textarea" rows={1} placeholder="(Optional) A description of what this job does" />
        </Col>
      </Form.Group>
      <Form.Group as={Row} className="mb-3">
        <Form.Label column sm={2}>Avionics Platform</Form.Label>
        <Col sm={10}>
          <Form.Select aria-label="Branch-select" onChange={(event) => {
              const [avName, repo, defaultBranch] = event.target.value.split(":");
              setAvionics(avName);
              setAvionicsRepo(repo);
              setDefaultBranch(defaultBranch);
            }}>
            <option value="none" data-repo="none">Select an avionics stack</option>
            <option value="TARS mkIV:TARS-Software:master">TARSmkIV</option>
            <option value="MIDAS mkI:MIDAS-Software:main">MIDASmkI</option>
          </Form.Select>
        </Col> 
      </Form.Group>

      <Form.Group as={Row} className="mb-3">
        <Form.Label column sm={2}>Select Branch</Form.Label>
        <Col sm={10}>
          {branchSelect}
        </Col> 
      </Form.Group>

      <Form.Group as={Row} className="mb-3">
        <Col sm={{ span: 10, offset: 2 }}>
          {(avionics != "none" && selectedBranch != "none" && !submitting) ? <Button onClick={submitJob}>Submit</Button> : <Button disabled>Submit</Button>}
          {submitting ? <Spinner size="sm" className='submission-spinner' animation="border" role="status"></Spinner> : <></>}
          {error == "" ? <></> : <span className='error-text-submission'>Error while submitting job: {error}</span>}
        </Col>
      </Form.Group>
    </Form>
      </Card.Body>
    </Card>
  );
}

export default NewJob;