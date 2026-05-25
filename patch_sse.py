with open("src/ui/index.html", "r") as f:
    code = f.read()

old_sse = """          const chunk = decoder.decode(value);
          // Parse Server-Sent Events format
          const lines = chunk.split('\\n');
          for (let line of lines) {
              if (line.startsWith('data: ')) {
                  const data = JSON.parse(line.substring(6));
                  if (data.type === 'token') {
                      assistantDiv.innerHTML += data.text.replace(/\\n/g, '<br>');
                      ui.msgs.scrollTo({ top: ui.msgs.scrollHeight });
                  } else if (data.type === 'action') {
                      appendMessage("⚡ Executing CDP Action: " + data.action, 'msg-action');
                  }
              }
          }"""

new_sse = """          const chunk = decoder.decode(value, {stream: true});
          buffer += chunk;

          // Process fully received lines (split by double newline as per SSE spec)
          let messages = buffer.split('\\n\\n');
          // Keep the last incomplete fragment in the buffer
          buffer = messages.pop();

          for (let msg of messages) {
              const lines = msg.split('\\n');
              for (let line of lines) {
                  if (line.startsWith('data: ')) {
                      try {
                          const data = JSON.parse(line.substring(6));
                          if (data.type === 'token') {
                              assistantDiv.innerHTML += data.text.replace(/\\n/g, '<br>');
                              ui.msgs.scrollTo({ top: ui.msgs.scrollHeight });
                          } else if (data.type === 'action') {
                              appendMessage("⚡ Executing CDP Action: " + data.action, 'msg-action');
                          }
                      } catch (e) {
                          console.error("SSE JSON Parse Error:", e, "Payload:", line.substring(6));
                      }
                  }
              }
          }"""

code = code.replace(
    "const decoder = new TextDecoder('utf-8');",
    "const decoder = new TextDecoder('utf-8');\n        let buffer = '';"
).replace(old_sse, new_sse)

with open("src/ui/index.html", "w") as f:
    f.write(code)
