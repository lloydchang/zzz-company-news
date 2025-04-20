def generate_chatbot_js():
    """
    Generate the JavaScript code for the chatbot functionality
    
    Returns:
        JavaScript code as a string
    """
    return """
        document.addEventListener('DOMContentLoaded', () => {
            const chatToggle = document.querySelector('.chat-toggle-button');
            const chatContainer = document.querySelector('.chatbot-container');
            const closeChat = document.querySelector('.close-chat');
            const chatInput = document.querySelector('.chatbot-input input');
            const sendButton = document.querySelector('.chatbot-input button');
            const messagesContainer = document.querySelector('.chatbot-messages');
            
            setTimeout(() => {
                chatContainer.classList.add('active');
                chatToggle.style.display = 'none';
                chatInput.focus();
            }, 1000);
            
            chatToggle.addEventListener('click', () => {
                chatContainer.classList.add('active');
                chatToggle.style.display = 'none';
                chatInput.focus();
            });
            
            closeChat.addEventListener('click', () => {
                chatContainer.classList.remove('active');
                setTimeout(() => {
                    chatToggle.style.display = 'flex';
                }, 300);
            });
            
            function sendMessage() {
                const question = chatInput.value.trim();
                if (!question) return;
                
                addMessage(question, 'user');
                chatInput.value = '';
                
                if (handleFollowUp(question)) {
                    return;
                }
                
                conversationState.currentQuery = question;
                conversationState.mode = 'showing_results';
                conversationState.currentArticleIndex = 0;
                processQuery(question);
            }
            
            function addMessage(text, sender) {
                const message = document.createElement('div');
                message.classList.add('message');
                message.classList.add(sender + '-message');
                message.textContent = text;
                messagesContainer.appendChild(message);
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
            }
            
            function addMessageWithCitation(text, citation, url) {
                const messageContainer = document.createElement('div');
                
                const message = document.createElement('div');
                message.classList.add('message');
                message.classList.add('bot-message');
                message.textContent = text;
                
                // Create URL link element if URL is provided
                if (url && url !== "#") {
                    const linkElement = document.createElement('div');
                    linkElement.classList.add('source-link');
                    const link = document.createElement('a');
                    link.href = url;
                    link.target = "_blank"; // Open in new tab
                    link.textContent = url;
                    linkElement.appendChild(link);
                    messageContainer.appendChild(message);
                    messageContainer.appendChild(linkElement);
                } else {
                    // No URL, just add the message
                    messageContainer.appendChild(message);
                }
                
                messagesContainer.appendChild(messageContainer);
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
            }
            
            function processQuery(question) {
                const lowerQuestion = question.toLowerCase();
                
                if (DEBUG) {
                    console.log('Processing query:', question);
                    console.log('Available articles:', newsData.length);
                }
                
                const isCompanyQuery = lowerQuestion.split(' ').length <= 3;
                
                if (isCompanyQuery) {
                    const allCompanies = [...new Set(newsData.map(article => article.company.toLowerCase()))];
                    console.log('All companies:', allCompanies);
                    
                    const exactCompanyMatch = allCompanies.find(company => 
                        company.toLowerCase() === lowerQuestion.trim()
                    );
                    
                    const validPartialMatch = allCompanies.some(company => {
                        const companyWords = company.toLowerCase().split(/\\s+/);
                        const queryWords = lowerQuestion.toLowerCase().trim().split(/\\s+/);
                        
                        if (company.toLowerCase() === lowerQuestion.toLowerCase().trim()) {
                            return true;
                        }
                        
                        if (company.toLowerCase().includes(lowerQuestion.toLowerCase().trim())) {
                            return true;
                        }
                        
                        if (lowerQuestion.toLowerCase().trim().includes(company.toLowerCase())) {
                            return true;
                        }
                        
                        if (companyWords.length > 1) {
                            if (queryWords.includes(companyWords[0]) && companyWords[0].length > 3) {
                                return true;
                            }
                            
                            const companyPhrase = companyWords.join(' ');
                            const queryPhrase = queryWords.join(' ');
                            
                            for (let i = 0; i < companyWords.length - 1; i++) {
                                const phrase = companyWords[i] + ' ' + companyWords[i+1];
                                if (queryPhrase.includes(phrase)) {
                                    return true;
                                }
                            }
                        }
                        
                        return false;
                    });
                    
                    const companyExists = exactCompanyMatch !== undefined || validPartialMatch;
                    
                    if (!companyExists) {
                        addMessage(`I'm sorry, I don't have any news articles about "${lowerQuestion}". Would you like information about another company?`, 'bot');
                        conversationState.mode = 'initial';
                        return;
                    }
                }
                
                let keywords = [];
                
                const quoteRegex = /"([^"]+)"/g;
                let quoteMatch;
                while ((quoteMatch = quoteRegex.exec(question)) !== null) {
                    keywords.push(quoteMatch[1].toLowerCase());
                }
                
                const stopWords = new Set([
                    'a', 'an', 'the', 'and', 'or', 'but', 'is', 'are', 'was', 'were', 
                    'to', 'of', 'in', 'on', 'at', 'by', 'for', 'with', 'about', 'from',
                    'these', 'those', 'this', 'that', 'have', 'has', 'had', 'do', 'does',
                    'did', 'can', 'could', 'will', 'would', 'should', 'may', 'might'
                ]);
                
                const wordKeywords = lowerQuestion
                    .replace(/[^a-zA-Z0-9 ]/g, ' ')
                    .split(' ')
                    .filter(word => word.length > 2 && !stopWords.has(word.toLowerCase()));
                    
                keywords = [...keywords, ...wordKeywords];
                
                if (DEBUG) {
                    console.log('Extracted keywords:', keywords);
                }
                
                let relevantArticles = [];
                newsData.forEach(article => {
                    let score = 0;
                    const title = article.title.toLowerCase();
                    const body = article.body.toLowerCase();
                    const fullContent = article.full_content ? article.full_content.toLowerCase() : '';
                    const company = article.company.toLowerCase();
                    
                    if (company && lowerQuestion.includes(company)) {
                        score += 15;
                    }
                    
                    if (company && lowerQuestion.trim() === company) {
                        score += 30;
                    }
                    
                    if (company && lowerQuestion.trim().startsWith(company)) {
                        score += 25;
                    }
                    if (company && company.startsWith(lowerQuestion.trim())) {
                        score += 20;
                    }
                    
                    if (isCompanyQuery && company && !company.includes(lowerQuestion) && !lowerQuestion.includes(company)) {
                        const companyFirstWord = company.split(' ')[0].toLowerCase();
                        const queryFirstWord = lowerQuestion.trim().split(' ')[0].toLowerCase();
                        
                        if (companyFirstWord !== queryFirstWord) {
                            score -= 50;
                        }
                    }
                    
                    if (fullContent && fullContent.includes(lowerQuestion)) {
                        score += 10;
                    }
                    
                    keywords.forEach(keyword => {
                        if (company && keyword.length > 2 && company === keyword) {
                            score += 18;
                        }
                        else if (company && keyword.length > 2 && company.includes(keyword)) {
                            score += 5;
                        }
                        if (company && keyword.length > 2 && keyword.includes(company)) {
                            score += 10;
                        }
                        
                        if (title.includes(keyword)) score += 5;
                        if (body.includes(keyword)) score += 3;
                        
                        if (fullContent) {
                            if (keyword.length > 10 && fullContent.includes(keyword)) {
                                score += 8;
                            } else if (fullContent.includes(keyword)) {
                                score += 2;
                            }
                            
                            const keywordRegex = new RegExp(keyword, 'gi');
                            const occurrences = (fullContent.match(keywordRegex) || []).length;
                            score += Math.min(occurrences, 5) * 0.5;
                        }
                    });
                    
                    if (lowerQuestion.includes('who') || lowerQuestion.includes('person')) {
                        const nameRegex = /([A-Z][a-z]+ [A-Z][a-z]+)/g;
                        const names = fullContent ? (fullContent.match(nameRegex) || []) : [];
                        if (names.length > 0) score += 2;
                    }
                    
                    if (score > 0) {
                        if (DEBUG) {
                            console.log(`Article: ${article.title}, Score: ${score}`);
                        }
                        relevantArticles.push({...article, score});
                    }
                });
                
                relevantArticles.sort((a, b) => b.score - a.score);
                
                conversationState.relevantArticles = relevantArticles;
                conversationState.currentArticleIndex = 0;
                
                if (DEBUG) {
                    console.log('Relevant articles found:', relevantArticles.length);
                    if (relevantArticles.length > 0) {
                        console.log('Top article:', relevantArticles[0].title);
                        console.log('Top score:', relevantArticles[0].score);
                    }
                }
                
                if (relevantArticles.length > 0) {
                    const mostRelevant = relevantArticles[0];
                    let response = "";
                    
                    let informativeSnippet = '';
                    if (mostRelevant.full_content) {
                        const fullContent = mostRelevant.full_content;
                        
                        const paragraphs = fullContent.split(/\\n+/)
                            .filter(p => p.trim().length > 50);
                        
                        let foundRelevantSnippet = false;
                        for (const paragraph of paragraphs) {
                            const lowerPara = paragraph.toLowerCase();
                            const matchedKeywords = keywords.filter(kw => lowerPara.includes(kw));
                            
                            if (matchedKeywords.length >= 2) {
                                informativeSnippet = paragraph.trim().substring(0, 300) + '...';
                                foundRelevantSnippet = true;
                                break;
                            }
                        }
                        
                        if (!foundRelevantSnippet) {
                            for (const paragraph of paragraphs) {
                                if (keywords.some(keyword => paragraph.toLowerCase().includes(keyword))) {
                                    informativeSnippet = paragraph.trim().substring(0, 300) + '...';
                                    foundRelevantSnippet = true;
                                    break;
                                }
                            }
                        }
                        
                        if (!foundRelevantSnippet && fullContent.length > 0) {
                            if (fullContent.length > 500) {
                                const middleStart = Math.floor(fullContent.length / 3);
                                const middleContent = fullContent.substring(middleStart, middleStart + 500);
                                const sentences = middleContent.split(/[.!?] /).filter(s => s.length > 30);
                                
                                if (sentences.length > 0) {
                                    informativeSnippet = sentences[0].trim() + '...';
                                } else {
                                    informativeSnippet = fullContent.substring(0, 300) + '...';
                                }
                            } else {
                                informativeSnippet = fullContent.substring(0, 300) + '...';
                            }
                        }
                    }
                    
                    if (lowerQuestion.includes('what') && lowerQuestion.includes('company')) {
                        response = `Based on the news, ${mostRelevant.company} has been mentioned in relation to: "${mostRelevant.title}"`;
                    } else if (lowerQuestion.includes('latest') || lowerQuestion.includes('recent')) {
                        response = `The latest news I found is: "${mostRelevant.title}". ${mostRelevant.body.substring(0, 150)}...`;
                    } else if (informativeSnippet) {
                        response = `${informativeSnippet}`;
                    } else {
                        response = `${mostRelevant.title} ${mostRelevant.body.substring(0, 150)}`;
                    }
                    
                    addMessageWithCitation(response, `${mostRelevant.source}`, mostRelevant.url);
                    
                    if (relevantArticles.length > 1) {
                        setTimeout(() => {
                            addMessage(`I also found ${relevantArticles.length - 1} more articles that might be relevant. Would you like to know more about any specific topic?`, 'bot');
                            conversationState.mode = 'offering_more';
                        }, 1000);
                    }
                } else {
                    addMessage(`I couldn't find any information about that in the current news articles. Could you try asking something else?`, 'bot');
                    conversationState.mode = 'initial';
                }
            }
            
            const conversationState = {
                mode: 'initial',
                currentQuery: '',
                relevantArticles: [],
                currentArticleIndex: 0
            };
            
            function handleFollowUp(response) {
                const lowerResponse = response.toLowerCase().trim();
                
                if (conversationState.mode === 'offering_more' && 
                    (lowerResponse === 'yes' || lowerResponse === 'sure' || 
                     lowerResponse === 'ok' || lowerResponse.includes('yes'))) {
                    
                    if (conversationState.relevantArticles.length > conversationState.currentArticleIndex + 1) {
                        conversationState.currentArticleIndex++;
                        const nextArticle = conversationState.relevantArticles[conversationState.currentArticleIndex];
                        
                        let response = '';
                        if (nextArticle.full_content) {
                            const snippet = nextArticle.full_content.substring(0, 300) + '...';
                            response = `${snippet}`;
                        } else {
                            response = `${nextArticle.title}. ${nextArticle.body.substring(0, 150)}...`;
                        }
                        
                        addMessageWithCitation(response, `${nextArticle.source}`, nextArticle.url);
                        
                        const remaining = conversationState.relevantArticles.length - conversationState.currentArticleIndex - 1;
                        if (remaining > 0) {
                            setTimeout(() => {
                                addMessage(`I have ${remaining} more articles that might interest you. Would you like to see another one?`, 'bot');
                            }, 1000);
                        } else {
                            setTimeout(() => {
                                addMessage(`That's all the relevant articles I found. Is there something else you'd like to know about?`, 'bot');
                                conversationState.mode = 'initial';
                            }, 1000);
                        }
                        return true;
                    }
                }
                
                return false;
            }
            
            sendButton.addEventListener('click', sendMessage);
            chatInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') sendMessage();
            });
            
            chatToggle.style.display = 'none';
            chatToggle.style.opacity = '1';
            
            setTimeout(() => {
                chatToggle.classList.add('attention');
            }, 2000);
        });
    """
