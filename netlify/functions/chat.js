export async function handler(event) {
  try {
    const { message, dados } = JSON.parse(event.body);

    const prompt = `
Você é um assistente financeiro pessoal.

Dados do usuário:
- Entradas: ${dados.entradas}
- Saídas: ${dados.saidas}
- Saldo: ${dados.saldo}

Pergunta do usuário:
${message}

Responda de forma:
- Consultiva
- Levemente descontraída
- Educativa
- Direta
`;

    const response = await fetch("https://api.openai.com/v1/chat/completions", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${process.env.OPENAI_API_KEY}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        model: "gpt-4o-mini",
        max_tokens: 200,
        messages: [
          { role: "system", content: "Você é um especialista em finanças pessoais." },
          { role: "user", content: prompt }
        ]
      })
    });

    const data = await response.json();

    return {
      statusCode: 200,
      body: JSON.stringify({
        reply: data.choices[0].message.content
      })
    };

  } catch (error) {
    return {
      statusCode: 500,
      body: JSON.stringify({
        reply: "Erro ao processar 😢"
      })
    };
  }
}