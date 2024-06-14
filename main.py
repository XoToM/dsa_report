import re
import math
#import bisect

nodes = {}
all_paths = []

class NodePath:
	origin = None
	target = None
	distance = 0
	def __init__(self, origin, target, distance):
		self.origin = origin
		self.target = target
		self.distance = distance

class Node:
	name = ""
	paths = []
	visited = False
	lastNode = None
	cost = 0
	def __init__(self, name, paths=None):
		self.name = name
		self.paths = paths or []

		self.visited = False
		self.lastNode = None
		self.cost = 0


def heap_siftup(heap,index):	#	Heap list and the index of the element to sift up
    if len(heap) == 0:	#	Exits if the heap list is empty
        return -1

    while index > 0:
        parent = (index-1)//2	#	If the element is smaller than its parent swap them and repeat, otherwise return a value
        if heap[parent].cost > heap[index].cost:
            tmp = heap[parent]
            heap[parent] = heap[index]
            heap[index] = tmp
            index = parent
        else:
            break

    return index

def heap_siftdown(heap, index):
    if len(heap) == 0: #	If the heap list is empty we should return
        return -1

    while True:
        left = 2*index+1	#	Calculate the positions of the child elements in the heap list
        right = 2*index+2

        if left >= len(heap):	#	Return if the left-most element pointer is outside of the bounds of the list
            break

        smallest = left	#	Store the smaller element

        if right < len(heap) and heap[right].cost < heap[left].cost:	#	If the right element exists and is smaller than the left element we should update the variable above
            smallest = right

        if heap[index].cost > heap[smallest].cost:	#	If the smaller of the child elements is smaller than the current element we should swap them and repeat this loop, otherwise we should return
            tmp = heap[index]
            heap[index] = heap[smallest]
            heap[smallest] = tmp
            index = smallest
        else:
            break
    return index

def heap_insert(heap, value):
    index = len(heap)	#	Add an element at the end of the heap list, and sift it up to maintain the properties of the heap
    heap.append(value)
    return heap_siftup(heap, index)

def heap_extract_min(heap):
    if len(heap) == 0:	#	If the heap list is empty we shouldn't return anything
        return None

    result = heap[0]	#	Save the smallest element currently in the heap as the return value

    heap[0] = heap[len(heap)-1]	#	Replace the smallest element with the last element in the heap list

    heap.pop()	#	Make the heap list 1 element smaller

    heap_siftdown(heap, 0)	#	Sift down from the root node. This makes sure that the new root node didn't break the properties of the heap

    return result	#	Return


def generate_nodes():
	node_file = open("./Paths.txt", "r")

	lines = node_file.readlines()

	node_file.close()

	for line in lines:
		line = line.strip()

		extracted = re.split("\\s*(?:(?:->)|:)\\s*", line)
		src = extracted[0]
		dst = extracted[1]
		size = int(extracted[2])

		dst_node = None
		if dst not in nodes:
			dst_node = Node(dst)
			nodes[dst] = dst_node
		else:
			dst_node = nodes[dst]

		src_node = None
		if src not in nodes:
			src_node = Node(src)
			nodes[src] = src_node
		else:
			src_node = nodes[src]

		path = NodePath(src_node,dst_node,size)
		src_node.paths.append(path)
		all_paths.append(path)

	print("Node count: {}".format(len(nodes)))
	print("Path count: {}" .format(len(all_paths)))


def announce_results(dst):
	if not dst.visited:
		print("No path has been found")
	else:
		print("A path of length {} has been found.".format(dst.cost))
		steps = 0
		while dst is not None:
			steps += 1
			print(dst.name, end='')
			dst = dst.lastNode
			if dst is not None:
				print(" <- ", end='')
		print("")
		print("With {} steps in between".format(steps-1))



def djikstra(src):
	for _,n in nodes.items():	#	Reset the nodes to their default states
		n.visited = False
		n.lastNode = None
		n.cost = 0

	steps = 0
	openset = [src]		#	Set up the open set as an min heap binary tree. Initially it should only contain the starting node.
	while len(openset)>0:
		current = heap_extract_min(openset) #openset.pop()	#	Take the node with the smallest cost from the open set

		if current.visited:			#	We shouldn't visit this node if it already has been visited before
			continue

		current.visited = True	#	Mark the current node as visited

		for p in current.paths:		#	Check every path connected to this node
			steps += 1
			next = p.target
			if next.visited:	#	Skip paths to nodes which have already been visited
				continue

			new_cost = current.cost + p.distance	#	Recalculate the cost for this node

			if new_cost < next.cost or next.lastNode is None:	#	Update the target node of this path if using this path would decrease its cost, or if the target node hasn't been updated before
				next.cost = new_cost
				next.lastNode = current

				heap_insert(openset, next)	#	Add the node to the open set


	print("Steps: {}".format(steps))	#	Print out how many steps the algorithm took to find the shortest paths


def bellman_ford(src):
	#	Reset the program to initial values. The Bellman Ford algorithm requires that all nodes are set to infinity to mark them as unreachable.
	#	The only exception to this rule is the source node which should be marked with 0 instead.
	for _,n in nodes.items():
		n.visited = False
		n.lastNode = None
		n.cost = math.inf
	src.cost = 0

	steps = 0
	for _ in range(0, len(nodes)-1):	#	Repeat the following code as many times as there are vertices in the graph
		exit_early = True
		for p in all_paths:		#	Go through every edge in the graph and update the minimum path for every node in the graph
			steps += 1
			new_cost = p.origin.cost + p.distance	#	Calculate the new cost for the affected node
			if new_cost < p.target.cost:	#	If the new cost is smaller than the current cost we should update the node
				p.target.visited = True
				p.target.cost = new_cost
				p.target.lastNode = p.origin
				exit_early = False
		if exit_early:	#	If we haven't updated any nodes in this iteration then that means we are already finished, and we can exit the loop early
			break

	print("Steps: {}".format(steps))	#	Print out how many steps the algorithm took to find the shortest paths




generate_nodes()	#	Read the node data from the file


while True:
	#	Ask the user for the origin and destination node
	inp = ""
	while inp not in nodes:
		inp = input("Please enter the name of the origin node: ")

	start_node = nodes[inp]

	inp = ""
	while inp not in nodes:
		inp = input("Please enter the name of the destination node: ")

	end_node = nodes[inp]


	print("")
	print("--- Djikstra ---")	#	Run the Djikstra algorithm
	djikstra(start_node)
	announce_results(end_node)	#	Find a path to the destination node

	print("")
	print("--- Bellman Ford ---")	#	Run the Bellman Ford algorithm
	bellman_ford(start_node)
	announce_results(end_node)	#	Find a path to the destination node
