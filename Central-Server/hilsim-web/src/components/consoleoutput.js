import React, { useState } from 'react';
import { Card } from 'react-bootstrap';

function ConsoleOutputLine(props) {
    let padding = props.linePadding - (props.index.toString().length)
    // Pad using the unicode nbsp character, "\u00A0", NOT a regular space.
    return <span>
        <span className={'console-output-line' + (props.blur ? " blurred-text-gray" : "")}>{"\u00A0".repeat(padding) + props.index.toString()} |</span><span className={props.blur ? " blurred-text" : ""}> {props.text}</span>
    </span> 
}

function ConsoleOutput(props) {

    const [expanded, setExpanded] = useState(false)

    let output = props.hide ? ["There is no spoon!","You are worthy of great things :)","You should be proud of yourself.","Be patient, this too shall pass.","You are loved <3"] : props.output
    let linewidth = output.length.toString().length

    return (<Card className={"card-output"}>
        <Card variant={"top"} className={(expanded ? "" : "job-raw-output-container ") + "bg-dark text-white code-text" + (props.hide ? " user-select-none" : "")} style={{textAlign: 'left', padding: '5px'}}>
            {output.map((str, lineIndex) => {
                return <ConsoleOutputLine blur={props.hide} linePadding={linewidth} index={lineIndex+1} text={str} />
            })}
            <br/>
            <span className={'console-output-line' + (props.hide ? " blurred-text-gray" : "")}>( EOF )</span>


        </Card>
        <div className={'no-job-raw-output'  + (!props.hide ? " d-none" : "")}>
            This job does not have any output yet.
        </div>
        <div className={'extend-job-raw-output' + (props.hide ? " d-none" : "")} onClick={() => {setExpanded(!expanded)}}>
            {expanded ? "▲" : "▼"}
        </div>
    </Card>);
}

export { ConsoleOutput, ConsoleOutputLine }