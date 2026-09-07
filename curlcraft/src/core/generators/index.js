import { generateFetch } from './javascriptFetch.js';
import { generateAxios } from './javascriptAxios.js';
import { generateNodeFetch } from './nodeFetch.js';
import { generatePythonRequests } from './pythonRequests.js';
import { generatePythonHttpx } from './pythonHttpx.js';
import { generateGoHttp } from './goHttp.js';
import { generateRustReqwest } from './rustReqwest.js';
import { generatePhpCurl } from './phpCurl.js';
import { generateJavaHttpClient } from './javaHttpClient.js';
import { generateCsharpHttpClient } from './csharpHttpClient.js';
import { generateRubyNetHttp } from './rubyNetHttp.js';
import { generateHttpie } from './httpie.js';

export const TARGET_LANGUAGES = [
  {
    id: 'js-fetch',
    name: 'JavaScript',
    library: 'Fetch API',
    prismLang: 'javascript',
    extension: 'js',
    generator: generateFetch
  },
  {
    id: 'js-axios',
    name: 'JavaScript / TS',
    library: 'Axios',
    prismLang: 'javascript',
    extension: 'js',
    generator: generateAxios
  },
  {
    id: 'python-requests',
    name: 'Python',
    library: 'requests',
    prismLang: 'python',
    extension: 'py',
    generator: generatePythonRequests
  },
  {
    id: 'python-httpx',
    name: 'Python (Async)',
    library: 'httpx',
    prismLang: 'python',
    extension: 'py',
    generator: generatePythonHttpx
  },
  {
    id: 'node-fetch',
    name: 'Node.js',
    library: 'native fetch',
    prismLang: 'javascript',
    extension: 'js',
    generator: generateNodeFetch
  },
  {
    id: 'go-http',
    name: 'Go',
    library: 'net/http',
    prismLang: 'go',
    extension: 'go',
    generator: generateGoHttp
  },
  {
    id: 'rust-reqwest',
    name: 'Rust',
    library: 'reqwest',
    prismLang: 'rust',
    extension: 'rs',
    generator: generateRustReqwest
  },
  {
    id: 'php-curl',
    name: 'PHP',
    library: 'cURL',
    prismLang: 'php',
    extension: 'php',
    generator: generatePhpCurl
  },
  {
    id: 'java-http',
    name: 'Java',
    library: 'HttpClient',
    prismLang: 'java',
    extension: 'java',
    generator: generateJavaHttpClient
  },
  {
    id: 'csharp-http',
    name: 'C# / .NET',
    library: 'HttpClient',
    prismLang: 'csharp',
    extension: 'cs',
    generator: generateCsharpHttpClient
  },
  {
    id: 'ruby-net-http',
    name: 'Ruby',
    library: 'net/http',
    prismLang: 'ruby',
    extension: 'rb',
    generator: generateRubyNetHttp
  },
  {
    id: 'cli-httpie',
    name: 'CLI',
    library: 'HTTPie',
    prismLang: 'bash',
    extension: 'sh',
    generator: generateHttpie
  }
];

export function generateCode(languageId, parsedReq) {
  const target = TARGET_LANGUAGES.find(t => t.id === languageId) || TARGET_LANGUAGES[0];
  try {
    return target.generator(parsedReq);
  } catch (err) {
    return `// Failed to generate code for ${target.name} (${target.library}):\n// ${err.message}`;
  }
}
