import java.io.FileReader;
import java.io.BufferedReader;
import java.util.StringTokenizer;
import java.io.IOException;
import java.io.File;

class Pair<T1, T2>{
    protected T1 key;
    protected T2 value;
    public Pair(T1 key, T2 value) {
	this.key = key;
	this.value = value;
    }
    public T1 getKey() { return key; }
    public T2 getValue() { return value; }
}

public class TSPBenchmark{
    
    // load data from file
    private static Pair<TSPData, TSPSolution[]> loadFromFile(String fname)
	throws IOException {
	FileReader fr = new FileReader(fname);
	BufferedReader br = new BufferedReader(fr);
	String s;
	StringTokenizer st;
	int nsols = 0;
	int drow=0, srow=0;
	int n=0;
	int[][] d = new int[0][0];;
	int[][] tours = new int[0][0];
	while((s = br.readLine()) != null) {
	    int t = s.indexOf('#');
	    if (t != -1) s = s.substring(0, t);
	    st = new StringTokenizer(s);
	    if (st.countTokens() == 0) continue;
	    else if (n == 0 && st.countTokens() == 2) {
		n = Integer.parseInt(st.nextToken());
		d = new int[n][n];
		nsols = Integer.parseInt(st.nextToken());
		tours = new int[nsols][n+1];
	    } else if (drow < n) {
		int col = 0;
		while (st.hasMoreTokens()) {
		    d[drow][col++] = Integer.parseInt(st.nextToken());
		}
		drow += 1;
	    } else if (srow < nsols) {
		int col = 0;
		while (st.hasMoreTokens()) {
		    tours[srow][col++] = Integer.parseInt(st.nextToken());
		}
		srow += 1;
	    }
	}
	TSPData data = new TSPData(n, d);
	TSPSolution[] solutions = new TSPSolution[nsols];
	for (int i=0; i < nsols; i++) {
	    solutions[i] = new TSPSolution(data, tours[i]);
	}
	return new Pair<TSPData, TSPSolution[]>(data, solutions);
    }
    
    private static Pair<Integer, Double> parse_one(TSPSolution[] solutions) {
	int nimpr = 0;
	long totalLS = 0;
	long t1, t2;
	int n;
	for (int i=0; i < solutions.length; i++) {
	    t1 = System.nanoTime();
	    n = solutions[i].two_opt();
	    t2 = System.nanoTime();
	    totalLS += t2 - t1;
	    nimpr += n;
	}
	return new Pair<Integer, Double>(Integer.valueOf(nimpr),
					 Double.valueOf(totalLS/1e9));
    }
    
    private static void parse_many(String dirname, String benchmarkname) {
	File folder = new File(dirname);
	File[] filenames = folder.listFiles();
	for (int i=0; i < filenames.length; i++) {
	    String fname = filenames[i].toString();
	    String basename = fname.substring(1+fname.lastIndexOf("/"));
	    try {
		Pair<TSPData, TSPSolution[]> allData = loadFromFile(fname);
		TSPData d = allData.getKey();
		TSPSolution[] solutions = allData.getValue();
		Pair<Integer, Double> res = parse_one(solutions);
		System.out.println("java," + benchmarkname + "," + basename +
				   "," + d.n() + "," +
				   solutions.length + "," + res.getKey()
				   + "," + res.getValue());
	    } catch (IOException e) {
		System.err.println("Cannot open file " + fname);
	    }
	}
    }
    
    public static void main(String[] args) {
	if (args.length != 1) {
	    System.err.println("USAGE: java TSPBenchmark tsp_data_directory");
	    System.exit(2);
	}
	// System.out.println("#language,instance,n,nsolutions,n_improvements,CPU_2opt");
	parse_many(args[0], "2-opt");
    }
}
