import java.io.FileReader;
import java.io.BufferedReader;
import java.util.StringTokenizer;
import java.util.ArrayList;
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
	int[] d = new int[0];;
	ArrayList<ArrayList<Integer> > tours =
	    new ArrayList<ArrayList<Integer> >();
	while((s = br.readLine()) != null) {
	    int t = s.indexOf('#');
	    if (t != -1) s = s.substring(0, t);
	    st = new StringTokenizer(s);
	    if (st.countTokens() == 0) continue;
	    else if (n == 0 && st.countTokens() == 2) {
		n = Integer.parseInt(st.nextToken());
		d = new int[n*n];
		nsols = Integer.parseInt(st.nextToken());
	    } else if (drow < n) {
		int col = 0;
		while (st.hasMoreTokens()) {
		    d[n*drow+col++] = Integer.parseInt(st.nextToken());
		}
		drow += 1;
	    } else if (srow < nsols) {
		ArrayList<Integer> tour = new ArrayList<Integer>();
		while (st.hasMoreTokens()) {
		    tour.add(Integer.parseInt(st.nextToken()));
		}
		tours.add(tour);
	    }
	}
	TSPData data = new TSPData(n, d);
	TSPSolution[] solutions = new TSPSolution[nsols];
	for (int i=0; i < nsols; i++) {
	    solutions[i] = new TSPSolution(data, tours.get(i));
	}
	return new Pair<TSPData, TSPSolution[]>(data, solutions);
    }
    
    private static Pair<Integer, Double> benchmark_one(TSPSolution[] solutions,
						       String benchmarkname) {
	int nimpr = 0;
	long totalLS = 0;
	long t1, t2;
	int n = 0;
	for (int i=0; i < solutions.length; i++) {
	    t1 = System.nanoTime();
	    if (benchmarkname.equals("2-opt")) {
		n = solutions[i].two_opt();
	    } else if (benchmarkname.equals("Or-opt")) {
		n = solutions[i].or_opt();
	    } else if (benchmarkname.equals("lns")) {
		n = solutions[i].lns(10);
	    } else if (benchmarkname.equals("espprc")) {
		n = solutions[i].espprc(6, 1);
	    } else if (benchmarkname.equals("espprc-2")) {
		n = solutions[i].espprc(6, 2);
	    } else {
		System.err.println("Unknown benchmark: <" + benchmarkname +">");
		System.exit(2);
	    }
	    t2 = System.nanoTime();
	    totalLS += t2 - t1;
	    nimpr += n;
	}
	return new Pair<Integer, Double>(Integer.valueOf(nimpr),
					 Double.valueOf(totalLS/1e9));
    }
    
    private static void benchmark_many(String dirname, String benchmarkname) {
	File folder = new File(dirname);
	File[] filenames = folder.listFiles();
	for (int i=0; i < filenames.length; i++) {
	    String fname = filenames[i].toString();
	    String basename = fname.substring(1+fname.lastIndexOf("/"));
	    try {
		Pair<TSPData, TSPSolution[]> allData = loadFromFile(fname);
		TSPData d = allData.getKey();
		TSPSolution[] solutions = allData.getValue();
		Pair<Integer, Double> res = benchmark_one(solutions,
							  benchmarkname);
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
	if (args.length < 1) {
	    System.err.println("USAGE: java TSPBenchmark tsp_data_directory");
	    System.exit(2);
	}
	String benchmarkname = "2-opt";
	if (args.length > 1) {
	    benchmarkname = args[1];
	}
	// System.out.println("#language,instance,n,nsolutions,n_improvements,CPU_2opt");
	benchmark_many(args[0], benchmarkname);
    }
}
