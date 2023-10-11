import Container from 'react-bootstrap/Container';
import Nav from 'react-bootstrap/Nav';
import Navbar from 'react-bootstrap/Navbar';

function NavBar() {
  return (
    <>
      <Navbar bg="dark" data-bs-theme="dark">
        <Container>
          <Navbar.Brand href="#home">
            <img
              alt=""
              src={require("../../assets/images/ISS_logo.png")}
              width="30"
              height="30"
              className="d-inline-block align-top"
            />{' '}
            HILSIM
          </Navbar.Brand>
          <Nav className="me-auto">
            <Nav.Link href="#home">Home</Nav.Link>
            <Nav.Link href="#features">Queue</Nav.Link>
            <Nav.Link href="#pricing">About</Nav.Link>
            <Nav.Link href="#something">ISS</Nav.Link>
          </Nav>
        </Container>
        </Navbar>
    </>
  );
}

export default NavBar;