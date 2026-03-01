import java.util.Random;

public class example {
    private static final Random rand = new Random();
    
    public static void main(String[] args) {
        generateTestcase();
    }
    
    public static void generateTestcase() {
        // Random dimensions (within constraints)
        int n = rand.nextInt(49) + 2;  // 2 to 50
        int m = rand.nextInt(49) + 2;  // 2 to 50
        
        int k = rand.nextInt(99) + 2;  // 2 to 100
        int q = rand.nextInt(1000) + 1;  // 1 to 1000
        
        System.out.println(n + " " + m + " " + k + " " + q);
        
        // Generate initial ball colors
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < m; j++) {
                System.out.print((rand.nextInt(k) + 1) + " ");
            }
            System.out.println();
        }
        
        // Generate initial special effects (0-6)
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < m; j++) {
                // Higher chance for 0 (no effect)
                int effect;
                if (rand.nextDouble() < 0.7) {
                    effect = 0;
                } else {
                    effect = rand.nextInt(6) + 1;
                }
                System.out.print(effect + " ");
            }
            System.out.println();
        }
        
        // Generate q swap operations
        for (int i = 0; i < q; i++) {
            int x1 = rand.nextInt(n) + 1;
            int y1 = rand.nextInt(m) + 1;
            int x2, y2;
            
            // Ensure different positions for swap
            do {
                x2 = rand.nextInt(n) + 1;
                y2 = rand.nextInt(m) + 1;
            } while (x1 == x2 && y1 == y2);
            
            System.out.println(x1 + " " + y1 + " " + x2 + " " + y2);
        }
    }
}