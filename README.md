Sistema Interativo de Apoio ao Aprendizado Baseado em Questões: 
Uma Proposta para o Ensino Médio Tecnológico do IFPE

Este projeto apresenta o desenvolvimento do **Nexus IFPE**, um sistema interativo de apoio à resolução de questões. Concebido como uma iniciativa prática na disciplina de Introdução à Programação do curso de Análise e Desenvolvimento de Sistemas (ADS) do IFPE, o software visa oferecer uma ferramenta robusta para auxiliar os alunos do ensino médio do Instituto na revisão de conteúdos e preparação para avaliações. O sistema permite a prática de questões de diversas disciplinas e temas, fornecendo feedback imediato e registrando o desempenho do estudante.

## ⚙️ Arquitetura e Organização do Código

A arquitetura do Nexus IFPE foi desenvolvida com foco em **modularidade** e **Programação Orientada a Objetos (POO)**, garantindo um código organizado, de fácil manutenção e expansão.

### 2.1. Estrutura de Diretórios

O projeto segue uma estrutura lógica de diretórios para separar as responsabilidades:
* `assets/`: Arquivos de imagens utilizados ao longo do projeto.
* `data/`: Armazena os arquivos JSON, que servem como a camada de persistência para usuários, banco de questões e estatísticas.
* `ui/`: Contém os módulos Python gerados pelo Qt Designer.
* `gui/`: Contém os módulos Python gerados pelo Qt Designer, representando as interfaces visuais da aplicação.
* `main.py`: Atua como o módulo principal, orquestrando a lógica de negócio, a interação entre as interfaces e a manipulação de dados.

### 2.2. Gerenciamento de Dados

Os dados do sistema são persistidos em arquivos **JSON**, escolhidos pela sua flexibilidade e simplicidade para esta fase de desenvolvimento. São utilizados três arquivos principais:
* `users.json`: Gerencia as informações de autenticação e perfis dos usuários, incluindo seus papéis (e.g., "user", "admin").
* `questions.json`: Constitui o banco de questões, cada uma categorizada por disciplina e tema, com suas alternativas e resposta correta.
* `user_stats.json`: Registra o desempenho dos estudantes, com uma estrutura detalhada que permite analisar acertos e erros por disciplina e tema específicos.
Operações de leitura e escrita desses arquivos são centralizadas em funções dedicadas, com **tratamento de exceções** para garantir a robustez contra erros de I/O e formatação de dados.

### 2.3. Desenvolvimento da Interface Gráfica (GUI)

A interface do usuário foi construída utilizando a biblioteca **PyQt5**, que permite o desenvolvimento de aplicações desktop em Python. O **Qt Designer** foi empregado para a criação visual das telas, facilitando a separação entre o design e a lógica de programação. A comunicação entre os elementos da interface e o código-fonte é realizada através do mecanismo de **Sinais e Slots** do PyQt.

Para assegurar uma experiência de usuário consistente em diferentes ambientes, a interface foi projetada com **layouts adaptáveis**, utilizando gerenciadores de layout do PyQt em vez de posicionamento fixo, e configurando tamanhos de fonte em `pointSize` para melhor escalabilidade em telas com variadas configurações de DPI.

## ✨ Funcionalidades Essenciais Implementadas (Entrega Parcial)

Este protótipo do Nexus IFPE já incorpora as seguintes funcionalidades operacionais:

* **Sistema de Autenticação:**
    * Permite o login de usuários com validação de credenciais.
    * Implementa controle de acesso baseado em papel, restringindo a visibilidade de funcionalidades (ex: botão ADM) para perfis específicos.
* **Navegação e Fluxo do Usuário:**
    * Transição fluida entre a tela de login, menu principal e o módulo de questões.
* **Módulo de Resolução de Questões:**
    * **Carregamento e Exibição Dinâmica:** Questões são carregadas do `questions.json` e apresentadas na interface.
    * **Filtragem de Questões:** Um diálogo interativo permite ao usuário selecionar disciplinas e temas específicos para sua sessão de estudo, com opções populadas dinamicamente.
    * **Navegação no Quiz:** Suporte para avançar para a `próxima questão` e retornar à `questão anterior`.
    * **Visualização Aprimorada:** A área de texto da questão agora suporta **rolagem**, garantindo a leitura completa de enunciados extensos.
    * **Feedback Pedagógico Visual:**
        * Após confirmar a resposta, a alternativa selecionada é colorida (verde para correta, vermelho para incorreta).
        * Em caso de resposta incorreta, a **alternativa correta é também destacada em verde**, oferecendo feedback imediato para o aprendizado.
    * **Controle de Resposta:** As alternativas são desabilitadas e o botão de confirmação é bloqueado após a resposta, impedindo alterações. O histórico de respostas da sessão é mantido, e ao revisitar uma questão, a resposta anterior é exibida e as opções permanecem desabilitadas.
    * **Finalização de Quiz Inteligente:** Ao confirmar a resposta da última questão, o quiz é automaticamente encerrado, retornando o usuário ao menu principal de forma suave.
* **Atualização de Estatísticas:** A cada questão respondida, as estatísticas de desempenho do usuário são atualizadas no `user_stats.json`, registrando acertos, erros e percentuais por disciplina e tema.

## 🛠️ Como Executar o Projeto

Para executar o Nexus IFPE em seu ambiente local:

1.  **Instale as dependências:**
    ```bash
    pip install PyQt5
    ```
2.  **Execute a aplicação:**
    ```bash
    python main.py
    ```
