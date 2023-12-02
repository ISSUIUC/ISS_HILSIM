import Button from 'react-bootstrap/Button';
import Card from 'react-bootstrap/Card';
import { Container } from 'react-bootstrap';
import { useState, useRef } from 'react';
import Overlay from 'react-bootstrap/Overlay';

function QueueItem(props) {
  const [show, setShow] = useState(false);
  const target = useRef(null);
  
  return (
      <Card style={{textAlign: 'left', marginBottom: '10px'}}>
      <Card.Body>
        <Card.Title>{props.username}</Card.Title>
        <Card.Text>
          {props.description}
        </Card.Text>
        <Card.Text>
          Branch: {props.branch}
        </Card.Text>
        <Button variant="" className='text-white p-0' ref={target} onClick={() => setShow(!show)}>
          <p className='text-primary text-decoration-underline'>More</p>
        </Button>
      <Overlay target={target.current} show={show} placement="bottom" className='ml-2'>
        {({
          placement: _placement,
          arrowProps: _arrowProps,
          show: _show,
          popper: _popper,
          hasDoneInitialMeasure: _hasDoneInitialMeasure,
          ...props
        }) => (
          <div
            {...props}
            style={{
              position: 'absolute',
              backgroundColor: 'rgba(255, 100, 100, 0.85)',
              padding: '2px 10px',
              color: 'white',
              borderRadius: 3,
              ...props.style,
            }}
          >
            <Card.Text>
              Submit time {props.submit_time}
            </Card.Text>
          </div>
        )}
      </Overlay>
      </Card.Body>
    </Card>
  );
}

export default QueueItem;