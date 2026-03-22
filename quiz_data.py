# quiz_data.py

QUIZ_DATA = {
    "Computer Science": {
        1: [
            {"question": "What does CPU stand for?", "options": ["Central Process Unit", "Computer Personal Unit", "Central Processing Unit", "Central Processor Unit"], "answer": "Central Processing Unit"},
            {"question": "What is the main function of an operating system?", "options": ["Play games", "Manage hardware and software resources", "Edit photos", "Browse the internet"], "answer": "Manage hardware and software resources"},
            {"question": "What does RAM stand for?", "options": ["Read Access Memory", "Random Access Memory", "Run Access Memory", "Real Access Memory"], "answer": "Random Access Memory"},
            {"question": "Which of these is not an OS?", "options": ["Windows", "Linux", "Oracle", "macOS"], "answer": "Oracle"},
            {"question": "Which component is considered the 'brain' of the computer?", "options": ["Hard Drive", "CPU", "Monitor", "Motherboard"], "answer": "CPU"},
            {"question": "What is binary code?", "options": ["Code written by two people", "A system of 0s and 1s", "A programming language like Python", "Error codes"], "answer": "A system of 0s and 1s"},
            {"question": "What does HTTP stand for?", "options": ["HyperText Transfer Protocol", "HighText Transfer Protocol", "Hyper Transfer Text Protocol", "HyperText Transmission Protocol"], "answer": "HyperText Transfer Protocol"},
            {"question": "What is a bit?", "options": ["1024 bytes", "A string of text", "The smallest unit of data in a computer", "A part of a CPU"], "answer": "The smallest unit of data in a computer"},
            {"question": "What is an algorithm?", "options": ["A hardware component", "A step-by-step set of instructions", "A computer network", "A programming language"], "answer": "A step-by-step set of instructions"},
            {"question": "What does a compiler do?", "options": ["Deletes code", "Translates source code into machine code", "Writes code automatically", "Fixes hardware issues"], "answer": "Translates source code into machine code"}
        ],
        2: [
            {"question": "What is the time complexity of binary search?", "options": ["O(1)", "O(n)", "O(log n)", "O(n^2)"], "answer": "O(log n)"},
            {"question": "Which data structure uses LIFO?", "options": ["Queue", "Stack", "Tree", "Graph"], "answer": "Stack"},
            {"question": "Which sorting algorithm is typically the fastest on average?", "options": ["Bubble Sort", "Insertion Sort", "Merge Sort", "Selection Sort"], "answer": "Merge Sort"},
            {"question": "What characterizes a linked list?", "options": ["Contiguous memory allocation", "Nodes pointing to the next node", "Fixed size", "Direct access by index"], "answer": "Nodes pointing to the next node"},
            {"question": "In a database, what is a primary key?", "options": ["A password", "A unique identifier for a record", "The first column", "A foreign key"], "answer": "A unique identifier for a record"},
            {"question": "What does SQL stand for?", "options": ["Structured Query Language", "Standard Query Logic", "Simple Query Language", "System Query Language"], "answer": "Structured Query Language"},
            {"question": "What is abstraction in OOP?", "options": ["Hiding complex implementation details", "Copying code", "Deleting code", "Running code faster"], "answer": "Hiding complex implementation details"},
            {"question": "Which of these is a NoSQL database?", "options": ["MySQL", "PostgreSQL", "MongoDB", "SQLite"], "answer": "MongoDB"},
            {"question": "What is the main benefit of polymorphism?", "options": ["Security", "Code reusability and flexibility", "Speed", "Database management"], "answer": "Code reusability and flexibility"},
            {"question": "What is a hash table used for?", "options": ["Drawing tables", "Fast mapping of keys to values", "Sorting data", "Printing data"], "answer": "Fast mapping of keys to values"}
        ],
        3: [
            {"question": "What is the primary purpose of a mutex?", "options": ["Network routing", "Memory allocation", "Preventing race conditions", "Sorting strings"], "answer": "Preventing race conditions"},
            {"question": "What is tail recursion?", "options": ["Recursion at the start", "Recursion that is optimized iteratively", "Infinite recursion", "A design pattern"], "answer": "Recursion that is optimized iteratively"},
            {"question": "What is 'deadlock' in OS?", "options": ["When the computer turns off", "When two processes are waiting on each other indefinitely", "A slow network connection", "A full hard drive"], "answer": "When two processes are waiting on each other indefinitely"},
            {"question": "What differs a thread from a process?", "options": ["A process shares memory, a thread does not", "A thread is heavier", "Threads share the same memory space as the parent process", "There is no difference"], "answer": "Threads share the same memory space as the parent process"},
            {"question": "What is virtual memory?", "options": ["Memory on the cloud", "Using disk space to simulate extra RAM", "Cache memory", "Register memory"], "answer": "Using disk space to simulate extra RAM"},
            {"question": "What is a 'B-Tree' commonly used for?", "options": ["UI rendering", "Database indexing", "Network routing", "Sound processing"], "answer": "Database indexing"},
            {"question": "What does a hypervisor do?", "options": ["Speed up the CPU", "Manage virtual machines", "Connect to the internet", "Cool down the computer"], "answer": "Manage virtual machines"},
            {"question": "What is the difference between TCP and UDP?", "options": ["TCP is secure, UDP is not", "TCP is connection-oriented and reliable, UDP is connectionless", "They are the same", "UDP is only for local networks"], "answer": "TCP is connection-oriented and reliable, UDP is connectionless"},
            {"question": "What is 'P vs NP'?", "options": ["A hardware dispute", "A major unsolved problem in theoretical computer science", "A networking protocol", "A sorting algorithm"], "answer": "A major unsolved problem in theoretical computer science"},
            {"question": "What is a buffer overflow?", "options": ["When a cup is full", "A vulnerability where data exceeds memory boundaries", "When the CPU is too fast", "A database error"], "answer": "A vulnerability where data exceeds memory boundaries"}
        ]
    },
    "Data Science": {
        1: [
            {"question": "What is Pandas primarily used for?", "options": ["Web Development", "Data Manipulation", "Game Dev", "Networking"], "answer": "Data Manipulation"},
            {"question": "Which represents a categorical variable?", "options": ["Height", "Age", "Color", "Salary"], "answer": "Color"},
            {"question": "What does CSV stand for?", "options": ["Common Standard Variables", "Comma Separated Values", "Computer System Verification", "Core System Values"], "answer": "Comma Separated Values"},
            {"question": "What is the mode in statistics?", "options": ["The middle value", "The average value", "The most frequent value", "The largest value"], "answer": "The most frequent value"},
            {"question": "Which library is used for data visualization in Python?", "options": ["Numpy", "Pandas", "Matplotlib", "Scikit-learn"], "answer": "Matplotlib"},
            {"question": "What is a 'DataFrame'?", "options": ["A picture frame", "A 2D labeled data structure", "A type of database", "A neural network"], "answer": "A 2D labeled data structure"},
            {"question": "What is the mean?", "options": ["The most common number", "The maximum number", "The average", "The middle number"], "answer": "The average"},
            {"question": "What is data cleaning?", "options": ["Deleting all data", "Fixing or removing incorrect/corrupt data", "Formatting the hard drive", "Encrypting data"], "answer": "Fixing or removing incorrect/corrupt data"},
            {"question": "Which of these is a continuous variable?", "options": ["Eye color", "Number of siblings", "Temperature", "Zip code"], "answer": "Temperature"},
            {"question": "What does SQL stand for?", "options": ["Structured Query Language", "Standard Query Logic", "Simple Query Language", "System Query Language"], "answer": "Structured Query Language"}
        ],
        2: [
            {"question": "What is the range of a correlation coefficient?", "options": ["0 to 1", "-1 to 1", "0 to 100", "-100 to 100"], "answer": "-1 to 1"},
            {"question": "Which algorithm is used for Classification?", "options": ["Linear Regression", "K-Means", "Logistic Regression", "PCA"], "answer": "Logistic Regression"},
            {"question": "What is 'Overfitting'?", "options": ["When a model learns the training data too well, including noise", "When a model is too fast", "When the dataset is too small", "When a model fails to learn anything"], "answer": "When a model learns the training data too well, including noise"},
            {"question": "What does K-Means clustering do?", "options": ["Predicts a continuous value", "Groups unlabeled data into K clusters", "Finds the shortest path", "Visualizes data"], "answer": "Groups unlabeled data into K clusters"},
            {"question": "What is an outlier?", "options": ["A data point that differs significantly from others", "A missing value", "A duplicate value", "The most common value"], "answer": "A data point that differs significantly from others"},
            {"question": "What is cross-validation used for?", "options": ["Cleaning data", "Evaluating model performance and preventing overfitting", "Downloading data", "Extracting features"], "answer": "Evaluating model performance and preventing overfitting"},
            {"question": "In a confusion matrix, what is a False Positive?", "options": ["Correctly predicted true", "Correctly predicted false", "Predicted true, but actually false", "Predicted false, but actually true"], "answer": "Predicted true, but actually false"},
            {"question": "What does TF-IDF stand for?", "options": ["Text Format - Idea Data Format", "Term Frequency-Inverse Document Frequency", "Total Frequency-Index Document Format", "Test Framework-Integration Data Flow"], "answer": "Term Frequency-Inverse Document Frequency"},
            {"question": "What is 'Feature Engineering'?", "options": ["Building hardware", "Creating new input features from raw data", "Deleting features", "Testing features"], "answer": "Creating new input features from raw data"},
            {"question": "Which scalar scales features to a [0, 1] range?", "options": ["StandardScaler", "MinMaxScaler", "RobustScaler", "Normalizer"], "answer": "MinMaxScaler"}
        ],
        3: [
            {"question": "What does PCA stand for?", "options": ["Principal Component Analysis", "Primary Core Algorithm", "Predictive Classification Axis", "Part Component Analysis"], "answer": "Principal Component Analysis"},
            {"question": "What problem does L1 regularization (Lasso) address?", "options": ["Underfitting", "Feature Selection (drives weights to zero)", "Convergence speed", "Gradient Vanishing"], "answer": "Feature Selection (drives weights to zero)"},
            {"question": "What is 'Gradient Descent'?", "options": ["A way to visualize data", "An optimization algorithm to minimize the loss function", "A type of database", "A metric for accuracy"], "answer": "An optimization algorithm to minimize the loss function"},
            {"question": "What is the 'curse of dimensionality'?", "options": ["When data is 3D", "The difficulty of finding patterns as the number of features increases", "When a model is too slow", "When hard drives are full"], "answer": "The difficulty of finding patterns as the number of features increases"},
            {"question": "What is an ensemble method?", "options": ["Using one powerful model", "Combining multiple models to improve performance", "A data cleaning technique", "A type of scalar"], "answer": "Combining multiple models to improve performance"},
            {"question": "How does Random Forest prevent overfitting compared to Decision Trees?", "options": ["By training on all data", "By creating multiple trees and averaging them", "By ignoring small features", "By stopping early"], "answer": "By creating multiple trees and averaging them"},
            {"question": "What is 'Hyperparameter Tuning'?", "options": ["Changing the data", "Adjusting the settings of the training algorithm", "Tuning the database", "Modifying the output"], "answer": "Adjusting the settings of the training algorithm"},
            {"question": "What is an autoencoder used for?", "options": ["Translating text", "Unsupervised learning for dimensionality reduction or feature learning", "Sorting data", "Connecting to APIs"], "answer": "Unsupervised learning for dimensionality reduction or feature learning"},
            {"question": "What does the 'Kernel Trick' do in SVMs?", "options": ["Cleans data", "Projects data into a higher-dimensional space to make it linearly separable", "Reduces dimensions", "Speeds up the CPU"], "answer": "Projects data into a higher-dimensional space to make it linearly separable"},
            {"question": "What is SMOTE used for?", "options": ["Handling imbalanced datasets by generating synthetic samples", "Visualizing NLP data", "Regularizing models", "Deploying models"], "answer": "Handling imbalanced datasets by generating synthetic samples"}
        ]
    },
    "Business": {
        1: [
            {"question": "What does ROI stand for?", "options": ["Return on Investment", "Rate of Interest", "Return on Income", "Risk of Inflation"], "answer": "Return on Investment"},
            {"question": "Which is an asset?", "options": ["Loan", "Equipment", "Accounts Payable", "Tax"], "answer": "Equipment"},
            {"question": "What is the primary goal of a for-profit business?", "options": ["To spend money", "To maximize shareholder value/profit", "To hire people", "To pay taxes"], "answer": "To maximize shareholder value/profit"},
            {"question": "What does B2B mean?", "options": ["Back to Back", "Business to Business", "Bank to Bank", "Business to Buyer"], "answer": "Business to Business"},
            {"question": "What is a 'Startup'?", "options": ["A large corporation", "A newly emerged business venture", "A type of bank account", "A government agency"], "answer": "A newly emerged business venture"},
            {"question": "What does CEO stand for?", "options": ["Chief Executive Officer", "Chief Engineering Officer", "Central Executive Operations", "Core Ethical Officer"], "answer": "Chief Executive Officer"},
            {"question": "What is revenue?", "options": ["The total amount of money brought in by a company", "The company's debt", "The company's profit after taxes", "The cost of goods"], "answer": "The total amount of money brought in by a company"},
            {"question": "What is a target market?", "options": ["A place to shop", "The specific group of consumers a product is aimed at", "The stock market", "A competitor"], "answer": "The specific group of consumers a product is aimed at"},
            {"question": "What does HR stand for?", "options": ["Human Resources", "Huge Returns", "High Risk", "Hardware Requirements"], "answer": "Human Resources"},
            {"question": "What is a business plan?", "options": ["A receipt", "A document outlining a business's goals and how to achieve them", "An employee manual", "A tax form"], "answer": "A document outlining a business's goals and how to achieve them"}
        ],
        2: [
            {"question": "What describes 'Opportunity Cost'?", "options": ["Cost of raw materials", "Value of the next best alternative", "Marketing expense", "Fixed cost"], "answer": "Value of the next best alternative"},
            {"question": "In SWOT analysis, what does 'T' stand for?", "options": ["Time", "Talent", "Threats", "Taxes"], "answer": "Threats"},
            {"question": "What is economies of scale?", "options": ["Selling less for more", "Cost advantages reaped by companies when production becomes efficient", "Weighing products", "A HR term"], "answer": "Cost advantages reaped by companies when production becomes efficient"},
            {"question": "What is a KPI?", "options": ["Key Product Idea", "Key Performance Indicator", "Known Profit Index", "Key Person Insured"], "answer": "Key Performance Indicator"},
            {"question": "What does 'LTV' stand for in marketing?", "options": ["Lifetime Value", "Long Term Visa", "Low Time Variance", "Loan to Value"], "answer": "Lifetime Value"},
            {"question": "What is 'Churn Rate'?", "options": ["How fast butter is made", "The percentage of customers that stop using a company's product", "The rate of hiring", "The daily revenue"], "answer": "The percentage of customers that stop using a company's product"},
            {"question": "What is a USP?", "options": ["Unique Selling Proposition", "Universal Standard Product", "United States Patent", "Under Selling Price"], "answer": "Unique Selling Proposition"},
            {"question": "What is 'Liquidity'?", "options": ["The amount of water in an office", "How quickly an asset can be converted into cash", "The total debt", "The stock volume"], "answer": "How quickly an asset can be converted into cash"},
            {"question": "What is the break-even point?", "options": ["When a company closes", "When total revenues equal total costs", "When profits Double", "When the product launches"], "answer": "When total revenues equal total costs"},
            {"question": "What does 'B2C' mean?", "options": ["Business to Corporation", "Business to Consumer", "Bank to Consumer", "Buyer to Corporation"], "answer": "Business to Consumer"}
        ],
        3: [
            {"question": "What is the primary goal of the Six Sigma approach?", "options": ["Increase marketing", "Reduce defects and variability", "Hire more staff", "Rebrand the company"], "answer": "Reduce defects and variability"},
            {"question": "What does 'EBITDA' measure?", "options": ["Stock price", "Employee turnover", "Operating performance", "Marketing reach"], "answer": "Operating performance"},
            {"question": "What describes 'Venture Capital'?", "options": ["A bank loan", "Financing that investors provide to startup companies with long-term growth potential", "Money in a checking account", "A government grant"], "answer": "Financing that investors provide to startup companies with long-term growth potential"},
            {"question": "What is a 'Blue Ocean Strategy'?", "options": ["Investing in shipping", "Simultaneously pursuing differentiation and low cost to open up a new market space", "Copying competitors", "Lowering prices dramatically"], "answer": "Simultaneously pursuing differentiation and low cost to open up a new market space"},
            {"question": "What is Agile Project Management?", "options": ["A strict, rigid plan", "An iterative approach prioritizing flexibility and customer satisfaction", "A type of HR software", "A financial strategy"], "answer": "An iterative approach prioritizing flexibility and customer satisfaction"},
            {"question": "What is 'Goodwill' in accounting?", "options": ["Donating to charity", "An intangible asset associated with the purchase of one company by another", "A friendly company culture", "Free samples"], "answer": "An intangible asset associated with the purchase of one company by another"},
            {"question": "What does 'CAC' stand for in business metrics?", "options": ["Company Asset Control", "Customer Acquisition Cost", "Capital And Cash", "Client Account Center"], "answer": "Customer Acquisition Cost"},
            {"question": "What is the 'Lean Startup' methodology?", "options": ["Firing employees to save money", "Developing businesses and products using validated learning and experimentation", "Starting a business with no money", "A type of diet plan"], "answer": "Developing businesses and products using validated learning and experimentation"},
            {"question": "What is vertical integration?", "options": ["Building taller office buildings", "When a company owns or controls its suppliers, distributors, or retail locations", "Merging with a foreign company", "Hiring executives"], "answer": "When a company owns or controls its suppliers, distributors, or retail locations"},
            {"question": "What is an MVP (Minimum Viable Product)?", "options": ["The most valuable player", "A product with just enough features to satisfy early customers and provide feedback", "A failed product", "The final, perfect product version"], "answer": "A product with just enough features to satisfy early customers and provide feedback"}
        ]
    },
    "Artificial Intelligence": {
        1: [
            {"question": "What is machine learning?", "options": ["Writing raw code", "Computers learning from data", "Building hardware", "Networking"], "answer": "Computers learning from data"},
            {"question": "Which language is most popular for AI?", "options": ["Java", "C#", "Python", "Ruby"], "answer": "Python"},
            {"question": "What does CNN stand for in AI?", "options": ["Cable News Network", "Convolutional Neural Network", "Computed Neural Node", "Categorical Neural Network"], "answer": "Convolutional Neural Network"},
            {"question": "What is an algorithm?", "options": ["A robot", "A set of rules to be followed in calculations", "A dataset", "A hard drive"], "answer": "A set of rules to be followed in calculations"},
            {"question": "What is a dataset?", "options": ["A set of rules", "A collection of data used to train models", "A type of algorithm", "A computer virus"], "answer": "A collection of data used to train models"},
            {"question": "What does NLP stand for?", "options": ["Natural Language Processing", "Neuro Linguistic Programming", "New Logic Protocol", "Network Learning Phase"], "answer": "Natural Language Processing"},
            {"question": "What is the Turing Test?", "options": ["A test for driving", "A test of a machine's ability to exhibit intelligent behavior", "A hardware stress test", "A math exam"], "answer": "A test of a machine's ability to exhibit intelligent behavior"},
            {"question": "Which of these is an example of Narrow AI?", "options": ["A human-like robot", "Siri/Alexa", "A supercomputer taking over the world", "None of the above"], "answer": "Siri/Alexa"},
            {"question": "What is a Bot?", "options": ["A malicious user", "A software application that runs automated tasks", "A physical robot", "A type of file"], "answer": "A software application that runs automated tasks"},
            {"question": "What does AI stand for?", "options": ["Automated Intelligence", "Artificial Intelligence", "Advanced Interaction", "Applied Information"], "answer": "Artificial Intelligence"}
        ],
        2: [
            {"question": "What is the function of an activation function?", "options": ["Initialize weights", "Introduce non-linearity", "Delete unused neurons", "Save the model"], "answer": "Introduce non-linearity"},
            {"question": "Which is a type of Neural Network for sequences?", "options": ["CNN", "RNN", "MLP", "PCA"], "answer": "RNN"},
            {"question": "What is overfitting in Deep Learning?", "options": ["When the model is too big to fit in RAM", "When the model memorizes the training data but fails on new data", "When training stops too early", "When gradients vanish"], "answer": "When the model memorizes the training data but fails on new data"},
            {"question": "What is the role of the loss function?", "options": ["To speed up training", "To measure the error between prediction and actual target", "To format data", "To deploy the model"], "answer": "To measure the error between prediction and actual target"},
            {"question": "What is an epoch?", "options": ["A type of error", "One complete pass through the entire training dataset", "A specific node in a neural network", "A type of scalar"], "answer": "One complete pass through the entire training dataset"},
            {"question": "What is pooling in a CNN?", "options": ["Cleaning data", "Downsampling to reduce dimensions", "Adding more noise", "Generating images"], "answer": "Downsampling to reduce dimensions"},
            {"question": "What does a dropout layer do?", "options": ["Drops bad data", "Randomly disables neurons during training to prevent overfitting", "Deletes the model", "Logs errors"], "answer": "Randomly disables neurons during training to prevent overfitting"},
            {"question": "What is a tensor?", "options": ["A type of nerve", "A mathematical object analogous to but more general than a vector", "A memory stick", "A python library"], "answer": "A mathematical object analogous to but more general than a vector"},
            {"question": "Which framework was developed by Google?", "options": ["PyTorch", "TensorFlow", "Scikit", "MXNet"], "answer": "TensorFlow"},
            {"question": "What is transfer learning?", "options": ["Sending data over the internet", "Using a pre-trained model on a new, related problem", "A robot teaching a human", "Transferring code from Python to Java"], "answer": "Using a pre-trained model on a new, related problem"}
        ],
        3: [
            {"question": "What problem does Backpropagation solve?", "options": ["Data cleaning", "Calculating weight gradients by applying the chain rule", "Overfitting", "Deploying models"], "answer": "Calculating weight gradients by applying the chain rule"},
            {"question": "What is the 'vanishing gradient' problem?", "options": ["Models training too fast", "Gradients becoming too small to update early layers effectively", "Loss function missing", "GPUs crashing"], "answer": "Gradients becoming too small to update early layers effectively"},
            {"question": "What is an attention mechanism?", "options": ["An alert sound", "A technique allowing models to focus on specific parts of the input sequence", "A marketing term", "A type of activation function"], "answer": "A technique allowing models to focus on specific parts of the input sequence"},
            {"question": "What introduced the Transformer architecture?", "options": ["The 'Attention Is All You Need' paper", "The original Turing paper", "Google's 1998 patent", "The YOLO paper"], "answer": "The 'Attention Is All You Need' paper"},
            {"question": "What is a GAN?", "options": ["Generative Adversarial Network", "General AI Node", "Global Algorithm Network", "Gradient Aggregation Node"], "answer": "Generative Adversarial Network"},
            {"question": "In a GAN, what do the Generator and Discriminator do?", "options": ["They work together to clean data", "The Generator creates fake data; the Discriminator evaluates if it's real", "They compress large files", "They sort data"], "answer": "The Generator creates fake data; the Discriminator evaluates if it's real"},
            {"question": "What is reinforcement learning?", "options": ["Learning by reading", "Learning by interacting with an environment to maximize a reward", "Using larger datasets", "Supervised learning with more labels"], "answer": "Learning by interacting with an environment to maximize a reward"},
            {"question": "What does BERT stand for?", "options": ["Binary Encoding Random Trees", "Bidirectional Encoder Representations from Transformers", "Basic Entity Recognition Tool", "Big Engineering Research Team"], "answer": "Bidirectional Encoder Representations from Transformers"},
            {"question": "What is the 'exploding gradient' problem?", "options": ["When the computer overheats", "When gradients become exponentially large resulting in unstable weights", "When too much data is loaded", "When the loss is zero"], "answer": "When gradients become exponentially large resulting in unstable weights"},
            {"question": "What is 'Few-Shot Learning'?", "options": ["Training a model in a few seconds", "A model's ability to learn a new task given only a few examples", "Using only a few CPUs", "A technique limited to image recognition"], "answer": "A model's ability to learn a new task given only a few examples"}
        ]
    },
    "General": {
        1: [{"question": "What is the most critical skill for learning?", "options": ["Consistency", "Typing speed", "Buying expensive books", "Skipping modules"], "answer": "Consistency"} for _ in range(10)],
        2: [{"question": "What is the Pomodoro technique?", "options": ["A time management method", "A marketing strategy", "A database concept"], "answer": "A time management method"} for _ in range(10)],
        3: [{"question": "What defines 'First Principles' thinking?", "options": ["Breaking down complex problems into basic truths", "Memorization", "Guessing"], "answer": "Breaking down complex problems into basic truths"} for _ in range(10)]
    }
}

def get_questions_for_course(subject, level):
    topic = subject if subject in QUIZ_DATA else "General"
    safe_level = max(1, min(int(level), 3))
    return QUIZ_DATA[topic][safe_level]
