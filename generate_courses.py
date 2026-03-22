import mysql.connector
from db import get_connection

def generate_courses():
    courses = [
        # Programming & CS
        ("Python for Beginners", "Programming", "Beginner", "Learn the basics of Python programming, variables, loops, and functions from scratch.", None, None),
        ("Advanced Python Programming", "Programming", "Advanced", "Deep dive into object-oriented programming, decorators, generators, and async Python.", None, None),
        ("Introduction to Java", "Programming", "Beginner", "Master Java syntax, OOP concepts, and application development.", None, None),
        ("Data Structures & Algorithms", "Computer Science", "Intermediate", "Essential algorithms and data structures for coding interviews and efficient software design.", None, None),
        ("Operating Systems Internals", "Computer Science", "Advanced", "Understand how modern operating systems manage memory, processes, and file systems.", None, None),
        ("Web Development Bootcamp", "Web Development", "Beginner", "Learn HTML, CSS, JavaScript, and build your first responsive website.", None, None),
        ("React.js Frontend Framework", "Web Development", "Intermediate", "Build modern, dynamic single-page applications using React, Hooks, and Redux.", None, None),
        
        # Data & AI
        ("Data Science Fundamentals", "Data Science", "Beginner", "Introduction to data analysis, pandas, matplotlib, and basic statistics.", None, None),
        ("Machine Learning A-Z", "Data Science", "Intermediate", "Learn regression, classification, clustering, and scikit-learn.", None, None),
        ("Deep Learning and Neural Networks", "AI", "Advanced", "Explore TensorFlow, PyTorch, CNNs for computer vision, and RNNs for natural language processing.", None, None),
        ("Introduction to SQL & Databases", "Data Science", "Beginner", "Write complex queries, design schemas, and manage relational databases.", None, None),
        ("Big Data with Apache Spark", "Data Science", "Advanced", "Process massive datasets using distributed computing and PySpark.", None, None),
        
        # Mathematics
        ("Calculus I: Limits and Derivatives", "Mathematics", "Beginner", "Foundation of calculus focusing on limits, continuity, and basic differentiation.", None, None),
        ("Linear Algebra for Machine Learning", "Mathematics", "Intermediate", "Vectors, matrices, eigenvalues, and their applications in data science and 3D graphics.", None, None),
        ("Probability and Statistics", "Mathematics", "Intermediate", "Distributions, hypothesis testing, and statistical inference for decision making.", None, None),
        ("Discrete Mathematics", "Mathematics", "Intermediate", "Logic, set theory, combinatorics, and graph theory for computer science.", None, None),
        
        # Business & Economics
        ("Microeconomics Principles", "Business", "Beginner", "Understand supply and demand, market structures, and consumer behavior.", None, None),
        ("Financial Accounting", "Business", "Beginner", "Learn to read balance sheets, income statements, and manage corporate finances.", None, None),
        ("Digital Marketing Strategy", "Marketing", "Intermediate", "SEO, SEM, social media marketing, and creating high-converting digital campaigns.", None, None),
        ("Product Management Essentials", "Business", "Intermediate", "Learn how to guide product lifecycle, write specs, and manage Agile teams.", None, None),
        ("Entrepreneurship 101", "Business", "Beginner", "From idea generation to fundraising and scaling your startup.", None, None),
        
        # Design & Arts
        ("UI/UX Design Masterclass", "Design", "Beginner", "Figma, wireframing, user research, and creating beautiful digital interfaces.", None, None),
        ("Graphic Design Principles", "Design", "Beginner", "Color theory, typography, composition, and Adobe Illustrator basics.", None, None),
        ("3D Modeling with Blender", "Design", "Intermediate", "Create 3D assets, textures, and animations for games and movies.", None, None),
        
        # Humanities
        ("World History: 20th Century", "History", "Beginner", "Major global events, wars, and political shifts of the 1900s.", None, None),
        ("Introduction to Psychology", "Psychology", "Beginner", "Understanding human behavior, cognitive processes, and mental health.", None, None),
        ("Creative Writing Workshop", "Literature", "Intermediate", "Develop narrative structures, character arcs, and compelling prose.", None, None),
        
        # Engineering
        ("Introduction to Circuit Design", "Engineering", "Intermediate", "Ohm's law, digital logic gates, and building basic electronic circuits.", None, None),
        ("Thermodynamics", "Engineering", "Advanced", "Laws of thermodynamics, heat transfer, and energy systems.", None, None),
        ("Mechanical Engineering Statics", "Engineering", "Intermediate", "Analysis of forces on rigid bodies in equilibrium.", None, None),
    ]

    print(f"Connecting to database...")
    con = get_connection()
    cur = con.cursor()

    print(f"Inserting {len(courses)} courses...")
    insert_query = """
    INSERT INTO courses (title, subject, level, description, image_url, youtube_link)
    VALUES (%s, %s, %s, %s, %s, %s)
    """

    count = 0
    for course in courses:
        # Check if course already exists to avoid duplicates
        cur.execute("SELECT id FROM courses WHERE title = %s", (course[0],))
        if not cur.fetchone():
            try:
                cur.execute(insert_query, course)
                count += 1
            except Exception as e:
                print(f"Error inserting {course[0]}: {e}")

    con.commit()
    con.close()
    print(f"Successfully inserted {count} new courses.")

if __name__ == "__main__":
    generate_courses()
