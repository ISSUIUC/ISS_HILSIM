import Container from 'react-bootstrap/Container';
import Nav from 'react-bootstrap/Nav';
import Navbar from 'react-bootstrap/Navbar';
import { Button } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import DevOnly from '../devonly';

function NavBar() {
  return (
    <>
      <Navbar bg="dark" data-bs-theme="dark">
        <Container fluid>
          <Link to="/" style={{textDecoration: "none"}}>
          <Navbar.Brand href="#home">
            <img
              alt=""
              src={require("../../assets/images/ISS_logo.png")}
              width="30"
              height="30"
              className="d-inline-block align-top"
            />{' '}
            Kamaji
            <DevOnly>
              <span className='kamajidev-card'>
                Dev
              </span>
            </DevOnly>
          </Navbar.Brand>
          </Link>
          <Nav className="me-auto">
            <Link to="/new_job">
              <Button variant="success">Submit New Job</Button>
            </Link>
          </Nav>

          <Nav className="nav-left-pad">
            <Link to="/jobs">
              <Button variant="secondary">Jobs</Button>
            </Link>
          </Nav>

          <DevOnly>
            <Nav className="nav-left-pad">
              <Link to="/testing_dash">
                <Button variant="secondary">Testing Dashboard</Button>
              </Link>
            </Nav>
          </DevOnly>
          <Navbar.Collapse className="justify-content-end">
          <Navbar.Text>
            Signed in as: <a href="#login">User</a>
          </Navbar.Text>
        </Navbar.Collapse>
        </Container>
        </Navbar>
    </>
  );
}

export default NavBar;