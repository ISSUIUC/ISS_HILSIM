import { useEffect, useState } from 'react';

function LoadingSpinner() {
    return <div class="lds-ring"><div></div><div></div><div></div><div></div></div>;
}

function KamajiTag(props) {
    let display_text = props.display.charAt(0).toUpperCase() + props.display.slice(1).toLowerCase();
    let loading_tag = props.variant == "pending" ? <LoadingSpinner /> : <></>


    return <span className={'badge badge-' + props.variant}>{display_text} {loading_tag}</span>
}

function KamajiJobTags(props) {
    let badge1 = <></>;
    let badge2 = <></>;

    switch (props.status) {
        case "QUEUED":
            badge1 = <KamajiTag display={"Queued"} variant={"queued"} />
            break;
        case "RUNNING":
            badge1 = <KamajiTag display={"In progress"} variant={"progress"} />
            badge2 = <KamajiTag display={"Running"} variant={"pending"} />
            break;
        case "SETUP_PRECOMPILE":
            badge1 = <KamajiTag display={"In progress"} variant={"progress"} />
            badge2 = <KamajiTag display={"Setup"} variant={"pending"} />
            break;
        case "SETUP_COMPILING":
            badge1 = <KamajiTag display={"In progress"} variant={"progress"} />
            badge2 = <KamajiTag display={"Compiling"} variant={"pending"} />
            break;
        case "CANCELED":
            badge1 = <KamajiTag display={"Error"} variant={"error"} />
            badge2 = <KamajiTag display={"Job canceled"} variant={"error"} />
            break;
        case "SUCCESS":
            badge1 = <KamajiTag display={"Success"} variant={"success"} />
            badge2 = <KamajiTag display={"Job run successfully"} variant={"success"} />
            break;
        case "FAILED_CRASHED":
            badge1 = <KamajiTag display={"Error"} variant={"error"} />
            badge2 = <KamajiTag display={"Runtime error"} variant={"error"} />
            break;
        case "FAILED_COMPILE_ERROR":
            badge1 = <KamajiTag display={"Error"} variant={"error"} />
            badge2 = <KamajiTag display={"Compilation error"} variant={"error"} />
            break;
        case "FAILED_TIMEOUT":
            badge1 = <KamajiTag display={"Error"} variant={"error"} />
            badge2 = <KamajiTag display={"Timed out"} variant={"error"} />
            break;
        case "FAILED_OTHER":
            badge1 = <KamajiTag display={"Error"} variant={"error"} />
            badge2 = <KamajiTag display={"Unknown error"} variant={"error"} />
            break;
        case "SETUP":
            badge1 = <KamajiTag display={"In progress"} variant={"progress"} />
            badge2 = <KamajiTag display={"Setup"} variant={"pending"} />
            break;
        default:
            break;

        
    }


    return <>{badge1} {badge2}</>;
}

export {KamajiTag, KamajiJobTags};