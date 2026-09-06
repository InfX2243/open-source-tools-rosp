import YAML from 'yaml';

/**
 * Converts JSON object or string to YAML string
 */
export function jsonToYAML(jsonObj) {
  try {
    const obj = typeof jsonObj === 'string' ? JSON.parse(jsonObj) : jsonObj;
    return YAML.stringify(obj);
  } catch (err) {
    return `# Error converting to YAML: ${err.message}`;
  }
}

/**
 * Converts JSON array of objects to CSV string
 */
export function jsonToCSV(jsonObj) {
  try {
    let obj = typeof jsonObj === 'string' ? JSON.parse(jsonObj) : jsonObj;

    if (!Array.isArray(obj)) {
      if (typeof obj === 'object' && obj !== null) {
        obj = [obj];
      } else {
        return 'Error: Input JSON must be an object or array of objects for CSV export.';
      }
    }

    if (obj.length === 0) return 'CSV: Empty Array';

    // Collect all unique keys across all objects
    const headers = Array.from(
      new Set(
        obj.reduce((keys, item) => {
          if (typeof item === 'object' && item !== null) {
            return keys.concat(Object.keys(item));
          }
          return keys;
        }, [])
      )
    );

    const csvRows = [];
    csvRows.push(headers.join(','));

    for (const row of obj) {
      const values = headers.map(header => {
        const val = row[header];
        if (val === undefined || val === null) return '""';
        const escaped = ('' + (typeof val === 'object' ? JSON.stringify(val) : val)).replace(/"/g, '""');
        return `"${escaped}"`;
      });
      csvRows.push(values.join(','));
    }

    return csvRows.join('\n');
  } catch (err) {
    return `Error converting to CSV: ${err.message}`;
  }
}

/**
 * Converts JSON object to XML string
 */
export function jsonToXML(jsonObj, rootName = 'root') {
  try {
    const obj = typeof jsonObj === 'string' ? JSON.parse(jsonObj) : jsonObj;

    function toXML(val, key) {
      if (val === null || val === undefined) {
        return `<${key}/>`;
      }
      if (Array.isArray(val)) {
        return val.map(item => toXML(item, key)).join('\n');
      }
      if (typeof val === 'object') {
        const children = Object.keys(val)
          .map(k => toXML(val[k], k))
          .join('\n  ');
        return `<${key}>\n  ${children}\n</${key}>`;
      }
      // Escaping special characters
      const strVal = String(val)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;');
      return `<${key}>${strVal}</${key}>`;
    }

    return `<?xml version="1.0" encoding="UTF-8"?>\n${toXML(obj, rootName)}`;
  } catch (err) {
    return `<!-- Error converting to XML: ${err.message} -->`;
  }
}

/**
 * Converts JSON to Javascript Object / ES6 code string
 */
export function jsonToJSObject(jsonObj) {
  try {
    const obj = typeof jsonObj === 'string' ? JSON.parse(jsonObj) : jsonObj;
    const jsonStr = JSON.stringify(obj, null, 2);
    // Unquote safe object keys for clean JS syntax
    const jsObj = jsonStr.replace(/"([a-zA-Z_$][a-zA-Z0-9_$]*)"\s*:/g, '$1:');
    return `const data = ${jsObj};`;
  } catch (err) {
    return `// Error converting to JS Object: ${err.message}`;
  }
}
