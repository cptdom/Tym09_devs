import React from 'react';
import './About.css'

const about = (props) => {
    return (
        <div className="About">
            <div className="Hedr">Tým RealQuik</div>
            <a href="https://www.linkedin.com/in/dominik-hartinger-b88879201/" target="_blank" rel="noreferrer"><div className="Thumb1">
                    <div className="Headshot" id="Dominik"></div>
                    <h3>Dominik</h3>
                    <p className="Pos">CEO</p>
                    <p>Front-end developer</p>
                </div>
            </a>
            <a href="https://www.linkedin.com/in/jachymdvorak/" target="_blank" rel="noreferrer"><div className="Thumb2">
                <div className="Headshot" id="Jachym"/>
                    <h3>Jáchym</h3><br/>
                    <p>Chief Data Scientist</p>
                    <p>Týmový pražák</p>
                </div>
            </a>
            <a href="https://www.linkedin.com/in/matejcermak/" target="_blank" rel="noreferrer"><div className="Thumb3">
                <div className="Headshot" id="Matej"/>
                    <h3>Matěj</h3>
                    <p className="Pos">CTO</p>
                    <p>Back-end developer</p>
                    <p>Data scientist</p>
                </div>
            </a>
            <a href="https://www.linkedin.com/in/michal-dupkala-46bb95164/" target="_blank" rel="noreferrer"><div className="Thumb4">
                <div className="Headshot" id="Michal"/>
                    <h3>Michal</h3>
                    <p className="Pos">COO</p>
                    <p>Data Engineer</p>
                    <p>týmový Slovák</p>
                </div>
            </a>
            <a href="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcS3ZJpNtlUZatZVTHpAJRB8Wsu_tGjmPe15Hg&usqp=CAU" target="_blank" rel="noreferrer"><div className="Thumb5">
                <div className="Headshot" id="Pavel"/>
                <h3>Pavel</h3><br/>
                <p>Database expert</p>
                <p>Data Engineer</p>
                </div>
            </a>
        </div>
    );
};

export default about;