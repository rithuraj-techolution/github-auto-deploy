diff_examples = """<Example>
Example Input -

Original Code:

```code
function factorialIterative(n) {
    if (n < 0) {
        return "Factorial is not defined for negative numbers";
    }
    let result = 1;
    for (let i = 1; i <= n; i++) {
        result *= i;
    }
    return result;
}

console.log(factorialIterative(5));

function isPrime(n) {
  if (n <= 1) return false;
  if (n <= 3) return true;
  if (n % 2 === 0 || n % 3 === 0) return false;
  for (let i = 5; i * i <= n; i += 6) {
    if (n % i === 0 || n % (i + 2) === 0) return false;
  }
  return true;
}

console.log(isPrime(11));
console.log(isPrime(15));
```


Changed Part:

```code
    Update factorial.js

diff --git a/factorial.js b/factorial.js
index f08b765..4613d40 100644
--- a/factorial.js
+++ b/factorial.js
@@ -24,3 +24,19 @@ function factorialRecursive(n) {
 }

 console.log(factorialRecursive(5));
+
+
+
+function isPrime(n) {
+  if (n <= 1) return false;
+  if (n <= 3) return true;
+  if (n % 2 === 0 || n % 3 === 0) return false;
+  for (let i = 5; i * i <= n; i += 6) {
+    if (n % i === 0 || n % (i + 2) === 0) return false;
+  }
+  return true;
+}
+
+console.log(isPrime(11));
+console.log(isPrime(15));
```


Example Output -

```refactored
function factorialIterative(n) {
    if (n < 0) {
        return "Factorial is not defined for negative numbers";
    }
    let result = 1;
    for (let i = 1; i <= n; i++) {
        result *= i;
    }
    return result;
}

console.log(factorialIterative(5));

function isPrime(n) {
  // Check for non-prime numbers less than or equal to 3
  if (n <= 1) {
    return false; // 1 or less are not prime
  } else if (n <= 3) {
    return true; // 2 and 3 are prime
  }

  // Handle divisibility by 2 and 3 efficiently
  if (n % 2 === 0 || n % 3 === 0) {
    return false; // Divisible by 2 or 3, not prime
  }

  // Only check for odd divisors greater than 3 (optimized)
  for (let i = 5; i * i <= n; i += 6) {
    // Check divisibility by i and i + 2 (efficiently checks divisibility by 6k ± 1)
    if (n % i === 0 || n % (i + 2) === 0) {
      return false; // Divisible by a number greater than 3, not prime
    }
  }

  // If no divisors found, number is prime
  return true;
}

console.log(isPrime(11)); // Output: true
console.log(isPrime(15)); // Output: false
```
</Example>
"""

json_example = """
<EXAMPLE>

Sample Input 1:
Original Code:
```code
import sys
import logging

class ExampleClass:
    def get_existing_solution_count(self, customer_inquiry_need_run_id):
        result = 0
        # Database execution code here...
        return result
```
Changed Part:
```code
commit 2e3f5c5b0a2b1c6f7a9c8d9e0f1g2h3i4j5
Author: John Doe <johndoe@example.com>
Date: Mon May 27 10:30:00 2024 -0400

    refactor: add docstrings and TODOs

diff --git a/example_class.py b/example_class.py
index ec91d18..1e5e242 100644
--- a/example_class.py
+++ b/example_class.py
@@ -1,6 +1,10 @@
 import sys
 import logging

+
 class ExampleClass:
     def get_existing_solution_count(self, customer_inquiry_need_run_id):
+        \"\"\"Retrieves the count of existing solutions for a given customer inquiry need run ID.\"\"\"
         result = 0
-        # Database execution code here...
+        # TODO: Implement database execution code
         return result
```
Sample Output 1:

```json
[
  {
    "class ExampleClass:": "class ExampleClass:\n    \"\"\"This is a comment\"\"\""
  },
  {
    "def get_existing_solution_count(self, customer_inquiry_need_run_id):": "def get_existing_solution_count(self, customer_inquiry_need_run_id):\n        \"\"\"Retrieves the count of existing solutions for a given customer inquiry need run ID.\"\"\""
  },
  {
    "# Database execution code here...": "# TODO: Implement database execution code"
  }
]
```

Sample Input 2:

Original Code:
```code
import math

def calculate():
    res = 0
    for i in range(10):
        res += 1
    if res > 5:
        print("Result is greater than 5")
    return res
```

Changed Part:
```code
commit 0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d
Author: Jane Smith <janesmith@example.com>
Date: Mon May 27 14:15:00 2024 -0700

    refactor: improve variable naming and add comments

diff --git a/calculator.py b/calculator.py
index ec91d18..1e5e242 100644
--- a/calculator.py
+++ b/calculator.py
@@ -1,10 +1,11 @@
 import math

-def calculate():
-    res = 0
+def calculate():
+    \"\"\"Calculates and returns the result.\"\"\"
+    result = 0
     for i in range(10):
-        res += 1
-    if res > 5:
+        result += 1
+    if result > 5:
         print("Result is greater than 5") # Inform the user if the result is greater than 5
-    return res
+    return result
```


Sample Output 2:

```json
[
  {
    "def calculate()": "def calculate():\n    \"\"\"Calculates and returns the result.\"\"\""
  },
  {
    "res = 0": "result = 0"
  },
  {
    "res += 1": "result += 1"
  },
  {
    "if res > 5": "if result > 5"
  },
  {
    "print(\"Result is greater than 5\")": "print(\"Result is greater than 5\")  # Inform the user if the result is greater than 5"
  },
  {
    "return res": "return result"
  }
]
```
<EXAMPLE>
"""


def get_general_prompt_examples(language):
    if language == "Python":
        general_examples = """Input Code:\n
    def calculatetotalprice(products_list):
        totalprice = 0
        for p in productslist:
            totalprice += p['cost'] * p['quantity']
        return totalprice
    products = [
        {'name': 'Product A', 'cost': 10, 'quantity': 2},
        {'name': 'Product B', 'cost': 15, 'quantity': 1},
        {'name': 'Product C', 'cost': 20, 'quantity': 3}
    ]
    totalprice = calculatetotalprice(products)
    print("Total Price:", totalprice)

    Refactored Code:

    ```refactored
    def calculate_total_price(products):
        \"\"\"
        Calculate the total price of a list of products.

        Args:
            products (list): A list of dictionaries representing products, each containing 'name', 'cost', and 'quantity' keys.

        Returns:
            float: The total price of all products.
        \"\"\"
        total_price = 0

        # Iterate through each product in the products list
        for product in products:
            # Calculate the total price by multiplying the cost of each product by its quantity
            total_price += product['cost'] * product['quantity']

        # Return the total price
        return total_price

    # List of products with name, cost, and quantity properties
    products = [
        {'name': 'Product A', 'cost': 10, 'quantity': 2},
        {'name': 'Product B', 'cost': 15, 'quantity': 1},
        {'name': 'Product C', 'cost': 20, 'quantity': 3}
    ]

    # Calculate the total price of all products
    total_price = calculate_total_price(products)

    # Output the total price
    print("Total Price:", total_price)
    ```
    """
    elif language == "Javascript":
        general_examples = """
    Example 2:
    JavaScript Input code:
    const express = require('express'); 
    const app = express();
    app.get('/', function(req, res) {
      res.send('Hello, Express with CommonJS syntax!');
    });

    const PORT = process.env.PORT || 3000;
    app.listen(PORT, function() {
      console.log('Server is running on port ' + PORT);
    });

    Refactored:

    ```refactored 
    // index.js
    import express from 'express'; // ES6 import syntax
    // Create an Express application
    const app = express();
    // Define a route
    app.get('/', function(req, res) {
      res.send('Hello, Express with ES6 modules and CommonJS syntax!');
    });
    // Start the server
    const PORT = process.env.PORT || 3000;
    app.listen(PORT, function() {
      console.log('Server is running on port ' + PORT);
    });

    ```
    """

    else:
        general_examples = """
    C# Input code:

    using System;

    namespace UnrefactoredCode
    {
        class Program
        {
            static void Main(string[] args)
            {
                int[] nums = { 1, 2, 3, 4, 5 };
                int sum = 0;
                foreach (int n in nums)
                {
                    sum += n;
                }
                Console.WriteLine("Sum of numbers: " + sum);
            }
        }
    }

    Refactored Code:

    ```refactored
    using System;

    namespace RefactoredCode
    {
        class Program
        {
            static void Main(string[] args)
            {
                // Define an array of numbers
                int[] numbers = { 1, 2, 3, 4, 5 };

                // Initialize a variable to store the sum of numbers
                int sum = 0;

                // Iterate through each number in the array and calculate the sum
                foreach (int number in numbers)
                {
                    sum += number;
                }

                // Output the sum of numbers to the console
                Console
    ```
    """
    return general_examples


def get_diff_prompt_examples():
    return diff_examples


def get_json_prompt_examples():
    return json_example


def get_feedback_prompt_examples(language):
    if language == "python":
        example = """Original Code:

1  def factorial_iterative(n):
2      if n < 0:
3          return "Factorial is not defined for negative numbers"
4      result = 1
5      for i in range(1, n + 1):
6          result *= i
7      return result
8  
9  print(factorial_iterative(5))  # Output: 120
10 
11 def factorial_recursive(n):
12     if n < 0:
13         return "Factorial is not defined for negative numbers"
14     if n == 0 or n == 1:
15         return 1
16     return n * factorial_recursive(n - 1)
17 
18 print(factorial_recursive(5))  # Output: 120

Initial Refactored Code:

1  def factorial(n, recursive=False):
2      if n < 0:
3          return "Factorial is not defined for negative numbers"
4      if recursive:
5          return factorial_recursive(n)
6      else:
7          return factorial_iterative(n)
8  
9  def factorial_iterative(n):
10      result = 1
11      for i in range(1, n + 1):
12          result *= i
13      return result
14 
15 def factorial_recursive(n):
16     if n == 0 or n == 1:
17         return 1
18     return n * factorial_recursive(n - 1)
19 
20 print(factorial(5))  # Output: 120
21 print(factorial(5, recursive=True))  # Output: 120

User Feedback:
Add another example for finding factorial of 4 in line number 22.

OUTPUT CODE:
Initial Refactored Code:

1  def factorial(n, recursive=False):
2      if n < 0:
3          return "Factorial is not defined for negative numbers"
4      if recursive:
5          return factorial_recursive(n)
6      else:
7          return factorial_iterative(n)
8  
9  def factorial_iterative(n):
10      result = 1
11      for i in range(1, n + 1):
12          result *= i
13      return result
14 
15 def factorial_recursive(n):
16     if n == 0 or n == 1:
17         return 1
18     return n * factorial_recursive(n - 1)
19 
20 print(factorial(5))  # Output: 120
21 print(factorial(5, recursive=True))  # Output: 120
22 print(factorial(4))  # Output: 24
23 print(factorial(4, recursive=True))  # Output: 24
"""
    else:
        example = """ Original Code:

1  function factorialIterative(n) {
2      if (n < 0) {
3          return "Factorial is not defined for negative numbers";
4      }
5      let result = 1;
6      for (let i = 1; i <= n; i++) {
7          result *= i;
8      }
9      return result;
10 }

11 console.log(factorialIterative(5)); // Output: 120

12 function factorialRecursive(n) {
13     if (n < 0) {
14         return "Factorial is not defined for negative numbers";
15     }
16     if (n === 0 || n === 1) {
17         return 1;
18     }
19     return n * factorialRecursive(n - 1);
20 }

21 console.log(factorialRecursive(5)); // Output: 120


Initial Refactored Code:
1  function factorial(n, recursive = false) {
2      if (n < 0) {
3          return "Factorial is not defined for negative numbers";
4      }
5      if (recursive) {
6          return factorialRecursive(n);
7      } else {
8          return factorialIterative(n);
9      }
10 }

11 function factorialIterative(n) {
12     let result = 1;
13     for (let i = 1; i <= n; i++) {
14         result *= i;
15     }
16     return result;
17 }

18 function factorialRecursive(n) {
19     if (n === 0 || n === 1) {
20         return 1;
21     }
22     return n * factorialRecursive(n - 1);
23 }

24 console.log(factorial(5)); // Output: 120
25 console.log(factorial(5, true)); // Output: 120


User Feedback:
Add another example for finding factorial of 4 in line number 26.


OUTPUT CODE:
Initial Refactored Code:
1  function factorial(n, recursive = false) {
2      if (n < 0) {
3          return "Factorial is not defined for negative numbers";
4      }
5      if (recursive) {
6          return factorialRecursive(n);
7      } else {
8          return factorialIterative(n);
9      }
10 }

11 function factorialIterative(n) {
12     let result = 1;
13     for (let i = 1; i <= n; i++) {
14         result *= i;
15     }
16     return result;
17 }

18 function factorialRecursive(n) {
19     if (n === 0 || n === 1) {
20         return 1;
21     }
22     return n * factorialRecursive(n - 1);
23 }

24 console.log(factorial(5)); // Output: 120
25 console.log(factorial(5, true)); // Output: 120
26 console.log(factorial(4)); // Output: 24
27 console.log(factorial(4, true)); // Output: 24"""

        return example
