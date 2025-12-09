import java.util.Scanner;

public class example {
    public static void main(String[] args) {
        // Create a Scanner object to read input
        Scanner scanner = new Scanner(System.in);
        int number = scanner.nextInt();
        
        // Calculate the doubled value
        int doubled = number * 2;
        
        // Output the result
        System.out.println("The doubled value is: " + doubled);
        
        // Close the scanner to prevent resource leak
        scanner.close();
    }
}