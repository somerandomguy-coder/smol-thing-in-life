import './style.css'

// import fileContents from '../../../../../../web/canvas/8_direction_move/index.html?raw'
import fileContents from './main.ts?raw'

console.log(fileContents);
console.log("hello world")

import { WebContainer } from '@webcontainer/api';

// Call only once
const webcontainerInstance = await WebContainer.boot();


const files = {
    "index.html": {
        file: {
            contents: `${fileContents}`
        }
    }
}

await webcontainerInstance.mount(files)

const file = await webcontainerInstance.fs.readFile('/index.html', 'utf-8');
console.log(file);




document.querySelector<HTMLDivElement>('#app')!.innerHTML = `
<section id="center">
    hello
</section>
`

