import { useEffect, useState } from 'react';

function DevOnly(props) {
    const [visible, setVisible] = useState(false)
    useEffect(() => {
        if (process.env.NODE_ENV && process.env.NODE_ENV === "development") {
            setVisible(true)
        }
    }, [])


    if(!visible) {
        return <></>
    }
    return <>{props.children}</>
}

export default DevOnly;